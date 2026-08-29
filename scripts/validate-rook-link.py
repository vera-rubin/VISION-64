#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import PurePosixPath

HEX_RE = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")

V0_PROBES = {"hostname", "date_utc", "tool_versions"}
V0_TOOLS = {"git", "rustc", "cargo", "qemu-system-x86_64", "python3"}

V1_CAPABILITIES = {
    "repo.read",
    "repo.task-write",
    "git.task-branch",
    "process.user",
    "tmux.manage",
    "runner.inspect",
    "runner.execute",
    "runner.manage",
    "qemu.execute",
    "artifact.collect",
    "tooling.install",
    "network.outbound",
    "worker.delegate",
    "github.issue.write",
    "github.pr.write",
    "computer.read",
    "computer.task-write",
}
V1_ACTION_OUTCOMES = {"pass", "fail", "blocked", "partial"}
V1_ARTIFACT_KINDS = {"log", "report", "diff", "benchmark", "test-output", "archive", "other"}
V1_HARD_LIMIT_KEYS = {
    "merge_protected_branches",
    "force_push",
    "rewrite_history",
    "read_secrets",
    "exfiltrate_secrets",
    "disable_security_controls",
    "destructive_host_ops",
    "self_modify_rook_link_trust",
}
PROTECTED_BRANCHES = {"main", "master", "trunk", "production", "prod", "release", "stable"}


class ValidationError(Exception):
    pass


def fail(msg):
    raise ValidationError(msg)


def exact_keys(obj, allowed, required):
    if not isinstance(obj, dict):
        fail("object required")
    unknown = set(obj) - set(allowed)
    missing = set(required) - set(obj)
    if unknown:
        fail("unknown field(s): " + ", ".join(sorted(unknown)))
    if missing:
        fail("missing field(s): " + ", ".join(sorted(missing)))


def full_sha(v, name):
    if not isinstance(v, str) or not HEX_RE.fullmatch(v):
        fail(f"{name} must be a full lowercase 40- or 64-hex commit ID")


def bounded_string(v, name, minimum=1, maximum=None):
    if not isinstance(v, str) or len(v) < minimum or (maximum is not None and len(v) > maximum):
        fail(f"invalid {name}")
    if "\x00" in v:
        fail(f"invalid {name}")


def unique_list(v, name, minimum=0, maximum=None):
    if not isinstance(v, list) or len(v) < minimum or (maximum is not None and len(v) > maximum):
        fail(f"invalid {name}")
    try:
        if len(v) != len(set(v)):
            fail(f"duplicate {name}")
    except TypeError:
        fail(f"invalid {name}")


def request_path(v):
    bounded_string(v, "request_path", 1, 512)
    if "\\" in v:
        fail("invalid request_path")
    p = PurePosixPath(v)
    if p.is_absolute() or any(x in ("", ".", "..") for x in p.parts):
        fail("invalid request_path")
    if len(p.parts) < 4 or p.parts[:3] != ("ops", "rook", "requests"):
        fail("request_path must be under ops/rook/requests/")
    if ".git" in p.parts or p.suffix != ".json":
        fail("invalid request_path")


def safe_work_branch(v):
    if v is None:
        return
    if not isinstance(v, str) or not BRANCH_RE.fullmatch(v):
        fail("invalid work_branch")
    if ".." in v or "//" in v or v.endswith("/") or v.startswith("/"):
        fail("invalid work_branch")
    if v.lower() in PROTECTED_BRANCHES:
        fail("protected work_branch forbidden")
    first = v.split("/", 1)[0].lower()
    if first in PROTECTED_BRANCHES:
        fail("protected work_branch namespace forbidden")
    if not any(v.startswith(prefix) for prefix in ("rook/", "task/", "chore/", "fix/", "feat/", "test/")):
        fail("work_branch must use an approved task namespace")


def validate_v0_request(r):
    exact_keys(
        r,
        {"schema", "request_id", "repository", "base_commit", "operation", "scope", "probe", "acknowledgement"},
        {"schema", "request_id", "repository", "base_commit", "operation", "scope", "probe", "acknowledgement"},
    )
    if r["schema"] != "rook-link.request.v1":
        fail("unsupported request schema")
    if not isinstance(r["request_id"], str) or not ID_RE.fullmatch(r["request_id"]):
        fail("invalid request_id")
    if not isinstance(r["repository"], str) or not REPO_RE.fullmatch(r["repository"]):
        fail("invalid repository")
    full_sha(r["base_commit"], "base_commit")
    if r["operation"] != "probe.environment.v1":
        fail("unsupported operation")
    exact_keys(r["scope"], {"mode", "allow_mutation", "delegate"}, {"mode", "allow_mutation", "delegate"})
    if r["scope"] != {"mode": "read-only", "allow_mutation": False, "delegate": False}:
        fail("scope must be exactly read-only/non-mutating/non-delegating")
    exact_keys(r["probe"], {"fields", "tools"}, {"fields", "tools"})
    fields = r["probe"]["fields"]
    tools = r["probe"]["tools"]
    unique_list(fields, "probe fields", 1)
    unique_list(tools, "probe tools")
    if not set(fields) <= V0_PROBES:
        fail("invalid probe fields")
    if not set(tools) <= V0_TOOLS:
        fail("invalid probe tools")
    if "tool_versions" not in fields and tools:
        fail("tools require tool_versions field")
    expected = f"rook-link:{r['request_id']}:probe.environment.v1:read-only"
    if r["acknowledgement"] != expected:
        fail("invalid acknowledgement")


def validate_v1_request(r):
    exact_keys(
        r,
        {"schema", "request_id", "repository", "base_commit", "operation", "objective", "capabilities", "execution", "constraints", "evidence", "acknowledgement"},
        {"schema", "request_id", "repository", "base_commit", "operation", "objective", "capabilities", "execution", "constraints", "evidence", "acknowledgement"},
    )
    if r["schema"] != "rook-link.request.v2":
        fail("unsupported request schema")
    if not isinstance(r["request_id"], str) or not ID_RE.fullmatch(r["request_id"]):
        fail("invalid request_id")
    if not isinstance(r["repository"], str) or not REPO_RE.fullmatch(r["repository"]):
        fail("invalid repository")
    full_sha(r["base_commit"], "base_commit")
    if r["operation"] != "orchestrate.task.v1":
        fail("unsupported operation")

    exact_keys(r["objective"], {"summary", "success_criteria"}, {"summary", "success_criteria"})
    bounded_string(r["objective"]["summary"], "objective.summary", 1, 2000)
    criteria = r["objective"]["success_criteria"]
    if not isinstance(criteria, list) or not 1 <= len(criteria) <= 16:
        fail("invalid success_criteria")
    for item in criteria:
        bounded_string(item, "success criterion", 1, 500)

    caps = r["capabilities"]
    unique_list(caps, "capabilities", 1)
    if not all(isinstance(x, str) for x in caps) or not set(caps) <= V1_CAPABILITIES:
        fail("unknown capability")
    capset = set(caps)

    exact_keys(
        r["execution"],
        {"mode", "max_runtime_minutes", "max_workers", "work_branch", "computer_roots"},
        {"mode", "max_runtime_minutes", "max_workers", "work_branch", "computer_roots"},
    )
    ex = r["execution"]
    if ex["mode"] != "autonomous":
        fail("execution mode must be autonomous")
    if not isinstance(ex["max_runtime_minutes"], int) or isinstance(ex["max_runtime_minutes"], bool) or not 1 <= ex["max_runtime_minutes"] <= 360:
        fail("invalid max_runtime_minutes")
    if not isinstance(ex["max_workers"], int) or isinstance(ex["max_workers"], bool) or not 0 <= ex["max_workers"] <= 8:
        fail("invalid max_workers")
    safe_work_branch(ex["work_branch"])
    roots = ex["computer_roots"]
    unique_list(roots, "computer_roots", 0, 8)
    for root in roots:
        bounded_string(root, "computer root", 1, 512)

    if "repo.task-write" in capset and "repo.read" not in capset:
        fail("repo.task-write requires repo.read")
    if "git.task-branch" in capset and "repo.read" not in capset:
        fail("git.task-branch requires repo.read")
    if "computer.task-write" in capset and "computer.read" not in capset:
        fail("computer.task-write requires computer.read")
    if {"repo.task-write", "git.task-branch"} & capset and ex["work_branch"] is None:
        fail("repository write/git capabilities require work_branch")
    if ex["work_branch"] is not None and not ({"repo.task-write", "git.task-branch"} & capset):
        fail("work_branch requires repository write/git capability")
    if {"computer.read", "computer.task-write"} & capset and not roots:
        fail("computer capabilities require explicit computer_roots")
    if roots and not ({"computer.read", "computer.task-write"} & capset):
        fail("computer_roots require computer capability")
    if "worker.delegate" in capset and ex["max_workers"] == 0:
        fail("worker.delegate requires positive max_workers")
    if "worker.delegate" not in capset and ex["max_workers"] != 0:
        fail("max_workers requires worker.delegate")

    exact_keys(r["constraints"], V1_HARD_LIMIT_KEYS, V1_HARD_LIMIT_KEYS)
    if any(r["constraints"][k] is not False for k in V1_HARD_LIMIT_KEYS):
        fail("mandatory hard limits may not be relaxed")

    exact_keys(
        r["evidence"],
        {"result_transport", "include_actions", "include_artifacts", "include_delegation", "max_excerpt_chars"},
        {"result_transport", "include_actions", "include_artifacts", "include_delegation", "max_excerpt_chars"},
    )
    ev = r["evidence"]
    if ev["result_transport"] != "github-issue-3" or ev["include_actions"] is not True or ev["include_delegation"] is not True:
        fail("invalid evidence contract")
    if not isinstance(ev["include_artifacts"], bool):
        fail("invalid include_artifacts")
    if not isinstance(ev["max_excerpt_chars"], int) or isinstance(ev["max_excerpt_chars"], bool) or not 0 <= ev["max_excerpt_chars"] <= 8000:
        fail("invalid max_excerpt_chars")

    expected = f"rook-link:{r['request_id']}:orchestrate.task.v1:autonomous"
    if r["acknowledgement"] != expected:
        fail("invalid acknowledgement")


def validate_request(r):
    if not isinstance(r, dict):
        fail("object required")
    schema = r.get("schema")
    if schema == "rook-link.request.v1":
        validate_v0_request(r)
    elif schema == "rook-link.request.v2":
        validate_v1_request(r)
    else:
        fail("unsupported request schema")


def validate_v0_result(x, req=None, expected_commit=None, expected_path=None):
    exact_keys(
        x,
        {"schema", "request_id", "repository", "request_commit", "request_path", "base_commit", "operation", "status", "started_at", "finished_at", "evidence"},
        {"schema", "request_id", "repository", "request_commit", "request_path", "base_commit", "operation", "status", "started_at", "finished_at", "evidence"},
    )
    if x["schema"] != "rook-link.result.v1":
        fail("unsupported result schema")
    if not isinstance(x["request_id"], str) or not ID_RE.fullmatch(x["request_id"]):
        fail("invalid request_id")
    if not isinstance(x["repository"], str) or not REPO_RE.fullmatch(x["repository"]):
        fail("invalid repository")
    full_sha(x["request_commit"], "request_commit")
    full_sha(x["base_commit"], "base_commit")
    request_path(x["request_path"])
    if x["operation"] != "probe.environment.v1":
        fail("unsupported operation")
    if x["status"] not in {"pass", "fail", "blocked"}:
        fail("invalid status")
    for k in ("started_at", "finished_at"):
        if not isinstance(x[k], str) or not TIME_RE.fullmatch(x[k]):
            fail(f"invalid {k}")
    exact_keys(x["evidence"], {"hostname", "date_utc", "tool_versions", "notes"}, set())
    tv = x["evidence"].get("tool_versions", {})
    if not isinstance(tv, dict) or not set(tv) <= V0_TOOLS or not all(isinstance(v, str) for v in tv.values()):
        fail("invalid tool_versions evidence")
    if req is not None:
        validate_v0_request(req)
        for rk, qk in (("request_id", "request_id"), ("repository", "repository"), ("base_commit", "base_commit"), ("operation", "operation")):
            if x[rk] != req[qk]:
                fail(f"result/request mismatch: {rk}")
    if expected_commit is not None and x["request_commit"] != expected_commit:
        fail("result/request mismatch: request_commit")
    if expected_path is not None and x["request_path"] != expected_path:
        fail("result/request mismatch: request_path")


def validate_v1_result(x, req=None, expected_commit=None, expected_path=None):
    exact_keys(
        x,
        {"schema", "request_id", "repository", "request_commit", "request_path", "base_commit", "operation", "status", "started_at", "finished_at", "capabilities_used", "summary", "actions", "artifacts", "git", "delegation"},
        {"schema", "request_id", "repository", "request_commit", "request_path", "base_commit", "operation", "status", "started_at", "finished_at", "capabilities_used", "summary", "actions", "artifacts", "git", "delegation"},
    )
    if x["schema"] != "rook-link.result.v2":
        fail("unsupported result schema")
    if not isinstance(x["request_id"], str) or not ID_RE.fullmatch(x["request_id"]):
        fail("invalid request_id")
    if not isinstance(x["repository"], str) or not REPO_RE.fullmatch(x["repository"]):
        fail("invalid repository")
    full_sha(x["request_commit"], "request_commit")
    full_sha(x["base_commit"], "base_commit")
    request_path(x["request_path"])
    if x["operation"] != "orchestrate.task.v1":
        fail("unsupported operation")
    if x["status"] not in V1_ACTION_OUTCOMES:
        fail("invalid status")
    for k in ("started_at", "finished_at"):
        if not isinstance(x[k], str) or not TIME_RE.fullmatch(x[k]):
            fail(f"invalid {k}")
    bounded_string(x["summary"], "summary", 1, 4000)

    used = x["capabilities_used"]
    unique_list(used, "capabilities_used")
    if not all(isinstance(v, str) for v in used) or not set(used) <= V1_CAPABILITIES:
        fail("unknown capability in result")
    usedset = set(used)

    actions = x["actions"]
    if not isinstance(actions, list) or len(actions) > 64:
        fail("invalid actions")
    for action in actions:
        exact_keys(action, {"capability", "description", "outcome", "evidence"}, {"capability", "description", "outcome", "evidence"})
        if action["capability"] not in V1_CAPABILITIES:
            fail("unknown action capability")
        if action["capability"] not in usedset:
            fail("action capability missing from capabilities_used")
        bounded_string(action["description"], "action description", 1, 1000)
        if action["outcome"] not in V1_ACTION_OUTCOMES:
            fail("invalid action outcome")
        ev = action["evidence"]
        if not isinstance(ev, list) or len(ev) > 16:
            fail("invalid action evidence")
        for excerpt in ev:
            bounded_string(excerpt, "action evidence", 0, 8000)

    artifacts = x["artifacts"]
    if not isinstance(artifacts, list) or len(artifacts) > 64:
        fail("invalid artifacts")
    for artifact in artifacts:
        exact_keys(artifact, {"kind", "locator", "sha256", "description"}, {"kind", "locator", "sha256", "description"})
        if artifact["kind"] not in V1_ARTIFACT_KINDS:
            fail("invalid artifact kind")
        bounded_string(artifact["locator"], "artifact locator", 1, 1024)
        digest = artifact["sha256"]
        if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            fail("invalid artifact sha256")
        bounded_string(artifact["description"], "artifact description", 0, 1000)

    exact_keys(x["git"], {"branch", "head_commit", "dirty"}, {"branch", "head_commit", "dirty"})
    git = x["git"]
    if git["branch"] is not None:
        safe_work_branch(git["branch"])
    if git["head_commit"] is not None:
        full_sha(git["head_commit"], "git.head_commit")
    if not isinstance(git["dirty"], bool):
        fail("invalid git.dirty")

    exact_keys(x["delegation"], {"used", "workers"}, {"used", "workers"})
    delegation = x["delegation"]
    if not isinstance(delegation["used"], bool) or not isinstance(delegation["workers"], list) or len(delegation["workers"]) > 8:
        fail("invalid delegation")
    for worker in delegation["workers"]:
        exact_keys(worker, {"name", "task", "status"}, {"name", "task", "status"})
        bounded_string(worker["name"], "worker name", 1, 64)
        bounded_string(worker["task"], "worker task", 1, 1000)
        if worker["status"] not in V1_ACTION_OUTCOMES:
            fail("invalid worker status")
    if delegation["used"] != bool(delegation["workers"]):
        fail("delegation.used must match worker list")

    if req is not None:
        validate_v1_request(req)
        for rk, qk in (("request_id", "request_id"), ("repository", "repository"), ("base_commit", "base_commit"), ("operation", "operation")):
            if x[rk] != req[qk]:
                fail(f"result/request mismatch: {rk}")
        granted = set(req["capabilities"])
        if not usedset <= granted:
            fail("result used capability not granted by request")
        for action in actions:
            if action["capability"] not in granted:
                fail("action used capability not granted by request")
        requested_branch = req["execution"]["work_branch"]
        if requested_branch is not None and git["branch"] != requested_branch:
            fail("result/request mismatch: work_branch")
        if delegation["used"] and "worker.delegate" not in granted:
            fail("delegation not granted by request")
        if len(delegation["workers"]) > req["execution"]["max_workers"]:
            fail("delegation exceeds worker budget")
        if not req["evidence"]["include_artifacts"] and artifacts:
            fail("artifacts returned when request disabled artifact return")
    if expected_commit is not None and x["request_commit"] != expected_commit:
        fail("result/request mismatch: request_commit")
    if expected_path is not None and x["request_path"] != expected_path:
        fail("result/request mismatch: request_path")


def validate_result(x, req=None, expected_commit=None, expected_path=None):
    if not isinstance(x, dict):
        fail("object required")
    schema = x.get("schema")
    if schema == "rook-link.result.v1":
        validate_v0_result(x, req, expected_commit, expected_path)
    elif schema == "rook-link.result.v2":
        validate_v1_result(x, req, expected_commit, expected_path)
    else:
        fail("unsupported result schema")


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("kind", choices=["request", "result"])
    p.add_argument("file")
    p.add_argument("--request")
    p.add_argument("--request-commit")
    p.add_argument("--request-path")
    a = p.parse_args()
    try:
        obj = load(a.file)
        if a.kind == "request":
            validate_request(obj)
            print("valid rook-link request")
        else:
            req = load(a.request) if a.request else None
            if (a.request_commit is None) != (a.request_path is None):
                fail("--request-commit and --request-path must be supplied together")
            if a.request_commit is not None:
                full_sha(a.request_commit, "expected request_commit")
                request_path(a.request_path)
            validate_result(obj, req, a.request_commit, a.request_path)
            print("valid rook-link result")
    except (OSError, json.JSONDecodeError, ValidationError) as e:
        print(f"invalid rook-link {a.kind}: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
