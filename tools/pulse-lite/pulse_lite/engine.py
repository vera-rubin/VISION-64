from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import time
from typing import Callable, Protocol

from .browser import BrowserAdapter, BrowserState
from .prompts import stuck_recovery_prompt, wake_prompt
from .state import SessionState, StateStore, WakeEvent, utc_now


class GhLike(Protocol):
    def matching_events(self, repository: str, issue: int, request_prefix: str, *, after_comment_id: int = 0) -> list[WakeEvent]: ...
    def redeliver(self, *, repository: str, workflow: str, ref: str, request_id: str, request_commit: str, request_path: str) -> None: ...


@dataclass(slots=True)
class CycleResult:
    action: str
    detail: str


def _parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _seconds_since(value: str | None, now: datetime) -> float | None:
    dt = _parse_utc(value)
    if dt is None:
        return None
    return max(0.0, (now - dt).total_seconds())


class PulseEngine:
    def __init__(
        self,
        store: StateStore,
        gh: GhLike,
        browser: BrowserAdapter,
        *,
        log: Callable[[str], None] | None = None,
    ) -> None:
        self.store = store
        self.gh = gh
        self.browser = browser
        self.log = log or (lambda _: None)

    def _save(self, state: SessionState) -> None:
        self.store.save(state)

    def _queue_new_results(self, state: SessionState) -> int:
        count = 0
        events = self.gh.matching_events(
            state.repository,
            state.result_issue,
            state.request_prefix,
            after_comment_id=state.last_seen_comment_id,
        )
        for event in events:
            if state.enqueue(event):
                count += 1
        if events:
            state.last_seen_comment_id = max(state.last_seen_comment_id, max(e.comment_id for e in events))
        return count

    @staticmethod
    def _reset_browser_liveness(state: SessionState) -> None:
        state.browser_generating_since = None
        state.browser_last_progress_at = None
        state.browser_last_progress_signature = None

    def _record_browser_liveness(self, state: SessionState, view: BrowserState, now: datetime) -> bool:
        """Return True only when generation is stale, unchanged, and over the configured threshold."""
        if not view.generating:
            self._reset_browser_liveness(state)
            return False

        now_s = now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        if state.browser_generating_since is None:
            state.browser_generating_since = now_s
            state.browser_last_progress_at = now_s
            state.browser_last_progress_signature = view.progress_signature
            return False

        if view.progress_signature and view.progress_signature != state.browser_last_progress_signature:
            state.browser_last_progress_signature = view.progress_signature
            state.browser_last_progress_at = now_s
            return False

        stale_for = _seconds_since(state.browser_last_progress_at or state.browser_generating_since, now)
        return stale_for is not None and stale_for >= state.stuck_seconds

    def _recover_chatgpt(self, state: SessionState) -> CycleResult:
        if not state.stuck_recovery_enabled:
            return CycleResult("stuck-detected", "recovery disabled")
        if state.recovery_budget_remaining <= 0:
            state.status = "paused"
            return CycleResult("stuck-detected", "recovery budget exhausted; paused")

        stopped, stop_reason = self.browser.stop_generation()
        self.log(f"recovery stop: {stopped} {stop_reason}")
        # If the stop control vanished between inspect and recovery, the server may have completed.
        # Reloading the exact conversation is still the safest first reconciliation step.
        reloaded, reload_reason = self.browser.reload_exact_conversation()
        if not reloaded:
            state.status = "paused"
            return CycleResult("recovery-blocked", reload_reason)

        post = self.browser.inspect()
        if not post.exact_page or not post.composer_present:
            state.status = "paused"
            return CycleResult("recovery-blocked", "page identity/composer ambiguous after reload")
        if post.generating:
            state.status = "paused"
            return CycleResult("recovery-blocked", "conversation still generating after stop/reload")
        if not post.composer_empty:
            return CycleResult("recovery-queued", "composer occupied after reload; human priority")

        ok, reason = self.browser.inject(stuck_recovery_prompt(state))
        if not ok:
            return CycleResult("recovery-queued", reason)

        state.recovery_budget_remaining -= 1
        state.last_injection_at = utc_now()
        state.last_injection_outcome = "stuck-recovery submitted"
        self._reset_browser_liveness(state)
        return CycleResult("recovered", "submitted deterministic stuck-turn recovery prompt")

    def _maybe_redeliver_rook(self, state: SessionState, now: datetime) -> CycleResult | None:
        outstanding = state.outstanding()
        if outstanding is None:
            return None
        if any(item.get("request_id") == outstanding.request_id for item in state.queue) or any(
            item.get("request_id") == outstanding.request_id for item in state.processed
        ):
            state.set_outstanding(None)
            return CycleResult("rook-result-seen", outstanding.request_id)

        age = _seconds_since(outstanding.delivered_at, now)
        if age is None or age < state.rook_timeout_seconds:
            return None
        if outstanding.redelivery_attempts >= 1:
            return CycleResult("rook-stuck", "exact pointer already redelivered once; user control required")
        if not state.redelivery_workflow or not state.redelivery_ref:
            return CycleResult("rook-stuck", "no redelivery hook configured")

        self.gh.redeliver(
            repository=state.repository,
            workflow=state.redelivery_workflow,
            ref=state.redelivery_ref,
            request_id=outstanding.request_id,
            request_commit=outstanding.request_commit,
            request_path=outstanding.request_path,
        )
        outstanding.redelivery_attempts += 1
        outstanding.delivered_at = utc_now()
        state.set_outstanding(outstanding)
        return CycleResult("rook-redelivered", "redelivered exact immutable request pointer once")

    def cycle(self) -> CycleResult:
        state = self.store.load()
        if state.status != "active":
            return CycleResult("idle", f"session status={state.status}")

        queued = self._queue_new_results(state)
        now = datetime.now(timezone.utc)

        rook_result = self._maybe_redeliver_rook(state, now)
        if rook_result and rook_result.action in {"rook-redelivered", "rook-stuck"}:
            self._save(state)
            return rook_result

        view = self.browser.inspect()
        if self._record_browser_liveness(state, view, now):
            result = self._recover_chatgpt(state)
            self._save(state)
            return result

        if state.wake_budget_remaining <= 0:
            state.status = "paused"
            self._save(state)
            return CycleResult("budget-exhausted", "normal wake budget exhausted; paused")

        if not state.queue:
            self._save(state)
            return CycleResult("waiting", f"queued_new={queued}")

        if not view.exact_page or not view.composer_present:
            self._save(state)
            return CycleResult("queued", "configured ChatGPT page/composer unavailable")
        if view.generating:
            self._save(state)
            return CycleResult("queued", "ChatGPT is generating")
        if not view.composer_empty:
            self._save(state)
            return CycleResult("queued", "user text present; human priority")

        event = state.pop_queue()
        assert event is not None
        ok, reason = self.browser.inject(wake_prompt(state, event))
        if not ok:
            state.queue.insert(0, asdict(event))
            self._save(state)
            return CycleResult("queued", reason)

        state.mark_processed(event.comment_id, event.request_id)
        state.wake_budget_remaining -= 1
        state.last_injection_at = utc_now()
        state.last_injection_outcome = "wake submitted"
        outstanding = state.outstanding()
        if outstanding and outstanding.request_id == event.request_id:
            state.set_outstanding(None)
        if state.wake_budget_remaining == 0:
            state.status = "paused"
        self._save(state)
        return CycleResult("woke-chatgpt", event.request_id)

    def run(self, interval_seconds: float = 5.0) -> None:
        while True:
            result = self.cycle()
            self.log(f"{utc_now()} {result.action}: {result.detail}")
            time.sleep(max(1.0, interval_seconds))
