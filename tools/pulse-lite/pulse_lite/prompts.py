from __future__ import annotations

from .state import SessionState, WakeEvent


def wake_prompt(state: SessionState, event: WakeEvent) -> str:
    remaining = max(0, state.wake_budget_remaining - 1)
    return (
        "PULSE micro-loop wake.\n"
        f"Session: {state.session_id}\n"
        f"ROOK LINK result ready for request: {event.request_id}\n"
        f"Canonical result bus: {state.repository} issue #{state.result_issue}\n"
        f"Automatic wakes remaining after this wake: {remaining}\n"
        "Fetch and validate canonical GitHub state yourself. Continue only the existing "
        "user-authored task. If this requires a new objective, architecture/product judgment, "
        "meaningful scope expansion, destructive/security-sensitive action, or the automatic "
        "budget is exhausted, stop and return control to the user."
    )


def stuck_recovery_prompt(state: SessionState) -> str:
    remaining = max(0, state.recovery_budget_remaining - 1)
    return (
        "PULSE stuck-turn recovery.\n"
        f"Session: {state.session_id}\n"
        f"Canonical project state: {state.repository}; ROOK LINK result bus issue #{state.result_issue}.\n"
        f"Recovery attempts remaining after this recovery: {remaining}\n"
        "The previous ChatGPT turn appeared locally stuck and this exact conversation was reloaded. "
        "Re-read canonical GitHub state before acting. First determine whether the previous turn already "
        "completed any side effects; do not repeat completed mutations. Continue only the existing "
        "user-authored task. If state is ambiguous, a new objective or architecture judgment is required, "
        "or you cannot verify idempotency, stop and return control to the user."
    )
