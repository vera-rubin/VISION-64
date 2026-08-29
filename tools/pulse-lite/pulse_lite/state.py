from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import shutil
import tempfile
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_state_dir() -> Path:
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA")
        if root:
            return Path(root) / "VISION64" / "pulse-lite"
    xdg = os.environ.get("XDG_STATE_HOME")
    if xdg:
        return Path(xdg) / "vision64" / "pulse-lite"
    return Path.home() / ".local" / "state" / "vision64" / "pulse-lite"


@dataclass(slots=True)
class WakeEvent:
    comment_id: int
    request_id: str
    schema: str
    request_commit: str | None = None
    request_path: str | None = None
    queued_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class OutstandingRequest:
    request_id: str
    request_commit: str
    request_path: str
    delivered_at: str
    redelivery_attempts: int = 0


@dataclass(slots=True)
class SessionState:
    session_id: str
    conversation_url: str
    repository: str
    result_issue: int
    request_prefix: str
    wake_budget_initial: int
    wake_budget_remaining: int
    cdp_url: str
    adapter_mode: str = "web"
    started_at: str = field(default_factory=utc_now)
    status: str = "active"
    last_seen_comment_id: int = 0
    processed: list[dict[str, Any]] = field(default_factory=list)
    queue: list[dict[str, Any]] = field(default_factory=list)
    last_injection_at: str | None = None
    last_injection_outcome: str | None = None
    stuck_recovery_enabled: bool = False
    stuck_seconds: int = 180
    recovery_budget_initial: int = 0
    recovery_budget_remaining: int = 0
    rook_timeout_seconds: int = 300
    redelivery_workflow: str | None = None
    redelivery_ref: str | None = None
    outstanding_request: dict[str, Any] | None = None
    browser_generating_since: str | None = None
    browser_last_progress_at: str | None = None
    browser_last_progress_signature: str | None = None

    def validate(self) -> None:
        if self.status not in {"active", "paused", "stopped", "completed"}:
            raise ValueError(f"invalid status: {self.status}")
        if self.adapter_mode not in {"web", "desktop"}:
            raise ValueError(f"invalid adapter_mode: {self.adapter_mode}")
        if not (1 <= self.wake_budget_initial <= 3):
            raise ValueError("wake_budget_initial must be 1..3")
        if not (0 <= self.wake_budget_remaining <= self.wake_budget_initial):
            raise ValueError("invalid wake_budget_remaining")
        if not (0 <= self.recovery_budget_remaining <= self.recovery_budget_initial <= 3):
            raise ValueError("invalid recovery budget")
        if self.result_issue <= 0:
            raise ValueError("result_issue must be positive")
        if not self.request_prefix:
            raise ValueError("request_prefix is required")
        if not self.conversation_url.startswith("https://chatgpt.com/"):
            raise ValueError("conversation_url must be an exact chatgpt.com https URL")
        if not (self.cdp_url.startswith("http://127.0.0.1:") or self.cdp_url.startswith("http://localhost:")):
            raise ValueError("cdp_url must be loopback HTTP")
        if self.stuck_seconds < 30:
            raise ValueError("stuck_seconds must be at least 30")
        if self.rook_timeout_seconds < 30:
            raise ValueError("rook_timeout_seconds must be at least 30")

    def seen(self, comment_id: int, request_id: str) -> bool:
        return any(
            item.get("comment_id") == comment_id and item.get("request_id") == request_id
            for item in self.processed
        )

    def mark_processed(self, comment_id: int, request_id: str) -> None:
        if not self.seen(comment_id, request_id):
            self.processed.append({"comment_id": comment_id, "request_id": request_id})
            self.processed = self.processed[-512:]
        self.last_seen_comment_id = max(self.last_seen_comment_id, comment_id)

    def enqueue(self, event: WakeEvent) -> bool:
        if self.seen(event.comment_id, event.request_id):
            return False
        if any(
            item.get("comment_id") == event.comment_id and item.get("request_id") == event.request_id
            for item in self.queue
        ):
            return False
        self.queue.append(asdict(event))
        self.queue.sort(key=lambda x: x["comment_id"])
        return True

    def pop_queue(self) -> WakeEvent | None:
        if not self.queue:
            return None
        return WakeEvent(**self.queue.pop(0))

    def outstanding(self) -> OutstandingRequest | None:
        if not self.outstanding_request:
            return None
        return OutstandingRequest(**self.outstanding_request)

    def set_outstanding(self, request: OutstandingRequest | None) -> None:
        self.outstanding_request = asdict(request) if request else None


class StateStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or default_state_dir()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "session.json"

    def load(self) -> SessionState:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        state = SessionState(**raw)
        state.validate()
        return state

    def save(self, state: SessionState) -> None:
        state.validate()
        self.root.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(asdict(state), indent=2, sort_keys=True) + "\n"
        fd, tmp_name = tempfile.mkstemp(prefix="session-", suffix=".json.tmp", dir=self.root)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, self.path)
        except Exception:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise

    def preserve_corrupt(self) -> Path | None:
        if not self.path.exists():
            return None
        backup = self.root / f"session.corrupt.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        shutil.copy2(self.path, backup)
        return backup

    def exists(self) -> bool:
        return self.path.exists()
