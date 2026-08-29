#!/usr/bin/env python3
import copy
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rook_validator", ROOT / "scripts" / "validate-rook-link.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

req_v0 = json.loads((ROOT / "ops" / "rook" / "examples" / "request-v1.json").read_text())
res_v0 = json.loads((ROOT / "ops" / "rook" / "examples" / "result-v1.json").read_text())
req_v1 = json.loads((ROOT / "ops" / "rook" / "examples" / "request-v2.json").read_text())
res_v1 = json.loads((ROOT / "ops" / "rook" / "examples" / "result-v2.json").read_text())
V1_REQUEST_COMMIT = "1111111111111111111111111111111111111111"
V1_REQUEST_PATH = "ops/rook/requests/rook-link-orchestrate-001.json"


def reject(label, fn):
    try:
        fn()
    except m.ValidationError:
        print("ok - rejects", label)
        return
    raise SystemExit("negative case unexpectedly passed: " + label)


m.validate_request(req_v0)
m.validate_result(res_v0, req_v0)
print("ok - canonical v0 request/result")

m.validate_request(req_v1)
m.validate_result(res_v1, req_v1, V1_REQUEST_COMMIT, V1_REQUEST_PATH)
print("ok - canonical v1 orchestration request/result")

# v0 stays fail-closed.
for label, mutate in [
    ("v0-unknown-operation", lambda x: x.__setitem__("operation", "shell.exec.v1")),
    ("v0-symbolic-ref", lambda x: x.__setitem__("base_commit", "main")),
    ("v0-bad-ack", lambda x: x.__setitem__("acknowledgement", "yes")),
    ("v0-mutation", lambda x: x["scope"].__setitem__("allow_mutation", True)),
    ("v0-delegation", lambda x: x["scope"].__setitem__("delegate", True)),
    ("v0-command-field", lambda x: x.__setitem__("command", "whoami")),
    ("v0-shell-field", lambda x: x.__setitem__("shell", "pwsh")),
]:
    q = copy.deepcopy(req_v0)
    mutate(q)
    reject(label, lambda q=q: m.validate_request(q))

r = copy.deepcopy(res_v0)
r["request_id"] = "other"
reject("v0-identity-mismatch", lambda: m.validate_result(r, req_v0))
r = copy.deepcopy(res_v0)
r["request_path"] = "ops/rook/requests/../evil.json"
reject("v0-path-traversal", lambda: m.validate_result(r, req_v0))

# v1 request authority cannot be expanded by unrecognized fields/capabilities or weakened constraints.
for label, mutate in [
    ("v1-unknown-capability", lambda x: x["capabilities"].append("host.root")),
    ("v1-duplicate-capability", lambda x: x["capabilities"].append(x["capabilities"][0])),
    ("v1-symbolic-ref", lambda x: x.__setitem__("base_commit", "HEAD")),
    ("v1-protected-main", lambda x: x["execution"].__setitem__("work_branch", "main")),
    ("v1-protected-main-namespace", lambda x: x["execution"].__setitem__("work_branch", "main/evil")),
    ("v1-unapproved-branch-namespace", lambda x: x["execution"].__setitem__("work_branch", "random/branch")),
    ("v1-command-field", lambda x: x.__setitem__("command", "rm -rf /")),
    ("v1-shell-field", lambda x: x.__setitem__("shell", "bash")),
    ("v1-relax-force-push", lambda x: x["constraints"].__setitem__("force_push", True)),
    ("v1-relax-secret-read", lambda x: x["constraints"].__setitem__("read_secrets", True)),
    ("v1-relax-security", lambda x: x["constraints"].__setitem__("disable_security_controls", True)),
    ("v1-relax-self-modify", lambda x: x["constraints"].__setitem__("self_modify_rook_link_trust", True)),
    ("v1-bad-ack", lambda x: x.__setitem__("acknowledgement", "approved")),
]:
    q = copy.deepcopy(req_v1)
    mutate(q)
    reject(label, lambda q=q: m.validate_request(q))

q = copy.deepcopy(req_v1)
q["capabilities"].remove("repo.read")
reject("v1-repo-write-without-read", lambda: m.validate_request(q))
q = copy.deepcopy(req_v1)
q["execution"]["work_branch"] = None
reject("v1-write-without-work-branch", lambda: m.validate_request(q))
q = copy.deepcopy(req_v1)
q["capabilities"].remove("worker.delegate")
reject("v1-workers-without-delegation", lambda: m.validate_request(q))
q = copy.deepcopy(req_v1)
q["execution"]["max_workers"] = 0
reject("v1-delegation-with-zero-workers", lambda: m.validate_request(q))
q = copy.deepcopy(req_v1)
q["capabilities"].append("computer.read")
reject("v1-computer-read-without-roots", lambda: m.validate_request(q))
q = copy.deepcopy(req_v1)
q["execution"]["computer_roots"] = ["C:\\Users\\natha\\Documents\\codex"]
reject("v1-roots-without-computer-capability", lambda: m.validate_request(q))
q = copy.deepcopy(req_v1)
q["capabilities"].extend(["computer.read", "computer.task-write"])
q["execution"]["computer_roots"] = ["C:\\Users\\natha\\Documents\\codex"]
m.validate_request(q)
print("ok - explicit computer scope accepted")

# v1 result must remain inside the exact immutable request grant.
r = copy.deepcopy(res_v1)
r["request_id"] = "other"
reject("v1-result-identity-mismatch", lambda: m.validate_result(r, req_v1, V1_REQUEST_COMMIT, V1_REQUEST_PATH))
r = copy.deepcopy(res_v1)
r["request_commit"] = "3333333333333333333333333333333333333333"
reject("v1-result-request-commit-mismatch", lambda: m.validate_result(r, req_v1, V1_REQUEST_COMMIT, V1_REQUEST_PATH))
r = copy.deepcopy(res_v1)
r["request_path"] = "ops/rook/requests/../evil.json"
reject("v1-result-path-traversal", lambda: m.validate_result(r, req_v1, V1_REQUEST_COMMIT, V1_REQUEST_PATH))
r = copy.deepcopy(res_v1)
r["request_path"] = "ops/rook/requests/other.json"
reject("v1-result-request-path-mismatch", lambda: m.validate_result(r, req_v1, V1_REQUEST_COMMIT, V1_REQUEST_PATH))
r = copy.deepcopy(res_v1)
r["capabilities_used"].append("github.pr.write")
reject("v1-result-ungranted-capability", lambda: m.validate_result(r, req_v1, V1_REQUEST_COMMIT, V1_REQUEST_PATH))
r = copy.deepcopy(res_v1)
r["actions"][0]["capability"] = "github.pr.write"
r["capabilities_used"].append("github.pr.write")
reject("v1-result-ungranted-action", lambda: m.validate_result(r, req_v1, V1_REQUEST_COMMIT, V1_REQUEST_PATH))
r = copy.deepcopy(res_v1)
r["git"]["branch"] = "rook/different-task"
reject("v1-result-work-branch-mismatch", lambda: m.validate_result(r, req_v1, V1_REQUEST_COMMIT, V1_REQUEST_PATH))
r = copy.deepcopy(res_v1)
r["delegation"]["workers"] = [
    {"name": f"Worker-{i}", "task": "bounded task", "status": "pass"} for i in range(4)
]
reject("v1-result-worker-budget", lambda: m.validate_result(r, req_v1, V1_REQUEST_COMMIT, V1_REQUEST_PATH))
r = copy.deepcopy(res_v1)
r["delegation"]["used"] = False
reject("v1-result-delegation-consistency", lambda: m.validate_result(r, req_v1, V1_REQUEST_COMMIT, V1_REQUEST_PATH))

# Artifact return obeys the request's evidence setting.
q = copy.deepcopy(req_v1)
q["evidence"]["include_artifacts"] = False
r = copy.deepcopy(res_v1)
reject("v1-result-artifacts-disabled", lambda: m.validate_result(r, q, V1_REQUEST_COMMIT, V1_REQUEST_PATH))

print("all rook-link tests passed")
