from __future__ import annotations

from dataclasses import dataclass

from pulse_lite.browser import BrowserState
from pulse_lite.engine import PulseEngine
from pulse_lite.state import OutstandingRequest, SessionState, StateStore, WakeEvent


class FakeGh:
    def __init__(self, events=None):
        self.events = list(events or [])
        self.redeliveries = []

    def matching_events(self, repository, issue, request_prefix, *, after_comment_id=0):
        return [e for e in self.events if e.comment_id > after_comment_id and e.request_id.startswith(request_prefix)]

    def redeliver(self, **kwargs):
        self.redeliveries.append(kwargs)


class FakeBrowser:
    def __init__(self, states):
        self.states = list(states)
        self.injected = []
        self.stops = 0
        self.reloads = 0

    def inspect(self):
        if len(self.states) > 1:
            return self.states.pop(0)
        return self.states[0]

    def inject(self, prompt):
        self.injected.append(prompt)
        return True, "submitted"

    def stop_generation(self):
        self.stops += 1
        return True, "stop requested"

    def reload_exact_conversation(self):
        self.reloads += 1
        return True, "reloaded"


def make_state(**overrides):
    values = dict(
        session_id="s1",
        conversation_url="https://chatgpt.com/c/test",
        repository="vera-rubin/VISION-64",
        result_issue=3,
        request_prefix="pulse-s1-",
        wake_budget_initial=2,
        wake_budget_remaining=2,
        cdp_url="http://127.0.0.1:9223",
    )
    values.update(overrides)
    return SessionState(**values)


def idle():
    return BrowserState(True, True, True, False, "idle", "ok")


def test_matching_result_wakes_once_and_decrements_budget(tmp_path):
    store = StateStore(tmp_path)
    store.save(make_state())
    gh = FakeGh([WakeEvent(10, "pulse-s1-turn01", "rook-link.result.v2", "a" * 40, "ops/rook/requests/x.json")])
    browser = FakeBrowser([idle()])
    result = PulseEngine(store, gh, browser).cycle()
    state = store.load()
    assert result.action == "woke-chatgpt"
    assert state.wake_budget_remaining == 1
    assert len(browser.injected) == 1
    assert "Canonical result bus" in browser.injected[0]
    assert state.seen(10, "pulse-s1-turn01")


def test_human_composer_text_blocks_wake(tmp_path):
    store = StateStore(tmp_path)
    store.save(make_state())
    gh = FakeGh([WakeEvent(11, "pulse-s1-turn01", "rook-link.result.v2")])
    browser = FakeBrowser([BrowserState(True, True, False, False, "idle", "user typing")])
    result = PulseEngine(store, gh, browser).cycle()
    state = store.load()
    assert result.action == "queued"
    assert state.wake_budget_remaining == 2
    assert not browser.injected
    assert len(state.queue) == 1


def test_budget_zero_pauses(tmp_path):
    store = StateStore(tmp_path)
    store.save(make_state(wake_budget_initial=1, wake_budget_remaining=1))
    gh = FakeGh([WakeEvent(12, "pulse-s1-turn01", "rook-link.result.v2")])
    browser = FakeBrowser([idle()])
    PulseEngine(store, gh, browser).cycle()
    state = store.load()
    assert state.wake_budget_remaining == 0
    assert state.status == "paused"


def test_stale_generation_recovers_without_consuming_normal_budget(tmp_path):
    store = StateStore(tmp_path)
    state = make_state(
        stuck_recovery_enabled=True,
        stuck_seconds=30,
        recovery_budget_initial=1,
        recovery_budget_remaining=1,
        browser_generating_since="2000-01-01T00:00:00Z",
        browser_last_progress_at="2000-01-01T00:00:00Z",
        browser_last_progress_signature="same",
    )
    store.save(state)
    browser = FakeBrowser([
        BrowserState(True, True, True, True, "same", "generating"),
        idle(),
    ])
    result = PulseEngine(store, FakeGh(), browser).cycle()
    state = store.load()
    assert result.action == "recovered"
    assert browser.stops == 1
    assert browser.reloads == 1
    assert len(browser.injected) == 1
    assert "stuck-turn recovery" in browser.injected[0]
    assert state.recovery_budget_remaining == 0
    assert state.wake_budget_remaining == 2


def test_rook_timeout_redelivers_exact_pointer_once(tmp_path):
    store = StateStore(tmp_path)
    state = make_state(
        rook_timeout_seconds=30,
        redelivery_workflow="rook-link-deliver.yml",
        redelivery_ref="task/6-pulse-lite-micro-loop",
    )
    state.set_outstanding(OutstandingRequest(
        request_id="pulse-s1-turn01",
        request_commit="a" * 40,
        request_path="ops/rook/requests/pulse-s1-turn01.json",
        delivered_at="2000-01-01T00:00:00Z",
    ))
    store.save(state)
    gh = FakeGh()
    result = PulseEngine(store, gh, FakeBrowser([idle()])).cycle()
    assert result.action == "rook-redelivered"
    assert len(gh.redeliveries) == 1
    assert gh.redeliveries[0]["request_commit"] == "a" * 40
    assert store.load().outstanding().redelivery_attempts == 1
