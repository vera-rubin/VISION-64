from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import uuid

from .browser import PlaywrightChatGPTAdapter, validate_cdp_url, validate_conversation_url
from .engine import PulseEngine
from .github_client import GhClient
from .prompts import stuck_recovery_prompt, wake_prompt
from .state import OutstandingRequest, SessionState, StateStore, WakeEvent, utc_now


def _store(args) -> StateStore:
    return StateStore(Path(args.state_dir).expanduser() if getattr(args, "state_dir", None) else None)


def _load_or_die(store: StateStore) -> SessionState:
    if not store.exists():
        raise SystemExit("no PULSE session exists; run `pulse start` first")
    try:
        return store.load()
    except Exception as exc:
        backup = store.preserve_corrupt()
        raise SystemExit(f"state is invalid; preserved at {backup}: {exc}") from exc


def _engine(store: StateStore, state: SessionState) -> PulseEngine:
    browser = PlaywrightChatGPTAdapter(state.cdp_url, state.conversation_url)
    return PulseEngine(store, GhClient(), browser, log=print)


def cmd_doctor(args) -> int:
    validate_conversation_url(args.conversation_url)
    validate_cdp_url(args.cdp_url)
    gh = GhClient()
    problems = []
    if not gh.auth_ok():
        problems.append("gh auth unavailable")
    elif not gh.can_read_repo(args.repository):
        problems.append(f"cannot read {args.repository}")
    try:
        view = PlaywrightChatGPTAdapter(args.cdp_url, args.conversation_url).inspect()
        if not view.exact_page:
            problems.append("exact configured ChatGPT page not found")
        if not view.composer_present:
            problems.append("ChatGPT composer not confidently identified")
    except Exception as exc:
        problems.append(f"browser check failed: {type(exc).__name__}: {exc}")
    store = _store(args)
    try:
        store.root.mkdir(parents=True, exist_ok=True)
        probe = store.root / ".doctor-write-test"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
    except Exception as exc:
        problems.append(f"state directory not writable: {exc}")
    if problems:
        for item in problems:
            print(f"FAIL: {item}")
        return 1
    print("PULSE doctor: ready")
    return 0


def cmd_start(args) -> int:
    validate_conversation_url(args.conversation_url)
    validate_cdp_url(args.cdp_url)
    if not 1 <= args.budget <= 3:
        raise SystemExit("--budget must be 1..3")
    if not 0 <= args.recovery_budget <= 3:
        raise SystemExit("--recovery-budget must be 0..3")
    session_id = args.session_id or uuid.uuid4().hex[:12]
    state = SessionState(
        session_id=session_id,
        conversation_url=args.conversation_url,
        repository=args.repository,
        result_issue=args.result_issue,
        request_prefix=args.request_prefix,
        wake_budget_initial=args.budget,
        wake_budget_remaining=args.budget,
        cdp_url=args.cdp_url,
        stuck_recovery_enabled=args.stuck_recovery,
        stuck_seconds=args.stuck_seconds,
        recovery_budget_initial=args.recovery_budget,
        recovery_budget_remaining=args.recovery_budget,
        rook_timeout_seconds=args.rook_timeout_seconds,
        redelivery_workflow=args.redelivery_workflow,
        redelivery_ref=args.redelivery_ref,
    )
    store = _store(args)
    store.save(state)
    print(f"started PULSE session {session_id}; wake budget={args.budget}; recovery budget={args.recovery_budget}")
    return 0


def cmd_status(args) -> int:
    state = _load_or_die(_store(args))
    public = asdict(state)
    print(json.dumps(public, indent=2, sort_keys=True))
    return 0


def _set_status(args, status: str) -> int:
    store = _store(args)
    state = _load_or_die(store)
    state.status = status
    if status == "stopped":
        state.queue.clear()
    store.save(state)
    print(f"session {state.session_id}: {status}")
    return 0


def cmd_resume(args) -> int:
    store = _store(args)
    state = _load_or_die(store)
    if args.budget is not None:
        if not 1 <= args.budget <= 3:
            raise SystemExit("--budget must be 1..3")
        state.wake_budget_initial = args.budget
        state.wake_budget_remaining = args.budget
    if args.recovery_budget is not None:
        if not 0 <= args.recovery_budget <= 3:
            raise SystemExit("--recovery-budget must be 0..3")
        state.recovery_budget_initial = args.recovery_budget
        state.recovery_budget_remaining = args.recovery_budget
    state.status = "active"
    store.save(state)
    print(f"session {state.session_id}: active")
    return 0


def cmd_once(args) -> int:
    store = _store(args)
    state = _load_or_die(store)
    result = _engine(store, state).cycle()
    print(f"{result.action}: {result.detail}")
    return 0


def cmd_run(args) -> int:
    store = _store(args)
    state = _load_or_die(store)
    try:
        _engine(store, state).run(args.interval)
    except KeyboardInterrupt:
        print("PULSE stopped by user")
    return 0


def cmd_dry_run(args) -> int:
    state = _load_or_die(_store(args))
    if args.recovery:
        print(stuck_recovery_prompt(state))
        return 0
    event = WakeEvent(
        comment_id=0,
        request_id=f"{state.request_prefix}turnXX",
        schema="rook-link.result.v2",
    )
    print(wake_prompt(state, event))
    return 0


def cmd_expect_rook(args) -> int:
    store = _store(args)
    state = _load_or_die(store)
    state.set_outstanding(
        OutstandingRequest(
            request_id=args.request_id,
            request_commit=args.request_commit,
            request_path=args.request_path,
            delivered_at=utc_now(),
        )
    )
    if args.workflow is not None:
        state.redelivery_workflow = args.workflow
    if args.ref is not None:
        state.redelivery_ref = args.ref
    store.save(state)
    print(f"tracking outstanding Rook request {args.request_id}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pulse", description="VISION-64 bounded ChatGPT micro-loop helper")
    p.add_argument("--state-dir", help="override local PULSE state directory")
    sub = p.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--conversation-url", required=True)
    doctor.add_argument("--cdp-url", default="http://127.0.0.1:9223")
    doctor.add_argument("--repository", default="vera-rubin/VISION-64")
    doctor.set_defaults(func=cmd_doctor)

    start = sub.add_parser("start")
    start.add_argument("--conversation-url", required=True)
    start.add_argument("--cdp-url", default="http://127.0.0.1:9223")
    start.add_argument("--repository", default="vera-rubin/VISION-64")
    start.add_argument("--result-issue", type=int, default=3)
    start.add_argument("--request-prefix", required=True)
    start.add_argument("--budget", type=int, default=2)
    start.add_argument("--session-id")
    start.add_argument("--stuck-recovery", action="store_true")
    start.add_argument("--stuck-seconds", type=int, default=180)
    start.add_argument("--recovery-budget", type=int, default=1)
    start.add_argument("--rook-timeout-seconds", type=int, default=300)
    start.add_argument("--redelivery-workflow")
    start.add_argument("--redelivery-ref")
    start.set_defaults(func=cmd_start)

    once = sub.add_parser("once")
    once.set_defaults(func=cmd_once)

    run = sub.add_parser("run")
    run.add_argument("--interval", type=float, default=5.0)
    run.set_defaults(func=cmd_run)

    status = sub.add_parser("status")
    status.set_defaults(func=cmd_status)

    pause = sub.add_parser("pause")
    pause.set_defaults(func=lambda a: _set_status(a, "paused"))

    resume = sub.add_parser("resume")
    resume.add_argument("--budget", type=int)
    resume.add_argument("--recovery-budget", type=int)
    resume.set_defaults(func=cmd_resume)

    stop = sub.add_parser("stop")
    stop.set_defaults(func=lambda a: _set_status(a, "stopped"))

    dry = sub.add_parser("dry-run")
    dry.add_argument("--recovery", action="store_true")
    dry.set_defaults(func=cmd_dry_run)

    expect = sub.add_parser("expect-rook")
    expect.add_argument("--request-id", required=True)
    expect.add_argument("--request-commit", required=True)
    expect.add_argument("--request-path", required=True)
    expect.add_argument("--workflow")
    expect.add_argument("--ref")
    expect.set_defaults(func=cmd_expect_rook)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
