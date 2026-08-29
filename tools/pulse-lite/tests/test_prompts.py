from __future__ import annotations

from pulse_lite.prompts import stuck_recovery_prompt, wake_prompt
from pulse_lite.state import SessionState, WakeEvent


def state():
    return SessionState(
        session_id="s1",
        conversation_url="https://chatgpt.com/c/test",
        repository="vera-rubin/VISION-64",
        result_issue=3,
        request_prefix="pulse-s1-",
        wake_budget_initial=2,
        wake_budget_remaining=2,
        cdp_url="http://127.0.0.1:9223",
        recovery_budget_initial=1,
        recovery_budget_remaining=1,
    )


def test_wake_prompt_is_pointer_only():
    prompt = wake_prompt(state(), WakeEvent(9, "pulse-s1-turn01", "rook-link.result.v2", "a" * 40, "ops/rook/requests/x.json"))
    assert "pulse-s1-turn01" in prompt
    assert "issue #3" in prompt
    assert "evidence" not in prompt.lower()
    assert "commands" not in prompt.lower()


def test_recovery_prompt_demands_idempotency_check():
    prompt = stuck_recovery_prompt(state())
    assert "previous ChatGPT turn appeared locally stuck" in prompt
    assert "do not repeat completed mutations" in prompt
    assert "return control to the user" in prompt
