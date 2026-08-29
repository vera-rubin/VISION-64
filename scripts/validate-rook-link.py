#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import PurePosixPath

HEX_RE = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ALLOWED_PROBES = {"hostname", "date_utc", "tool_versions"}
ALLOWED_TOOLS = {"git", "rustc", "cargo", "qemu-system-x86_64", "python3"}

class ValidationError(Exception): pass

def fail(msg): raise ValidationError(msg)

def exact_keys(obj, allowed, required):
    if not isinstance(obj, dict): fail("object required")
    unknown = set(obj) - set(allowed)
    missing = set(required) - set(obj)
    if unknown: fail("unknown field(s): " + ", ".join(sorted(unknown)))
    if missing: fail("missing field(s): " + ", ".join(sorted(missing)))

def full_sha(v, name):
    if not isinstance(v, str) or not HEX_RE.fullmatch(v): fail(f"{name} must be a full lowercase 40- or 64-hex commit ID")

def relpath(v, root, name):
    if not isinstance(v, str) or not v or "\\" in v or "\x00" in v: fail(f"invalid {name}")
    p = PurePosixPath(v)
    if p.is_absolute() or any(x in ("", ".", "..") for x in p.parts): fail(f"invalid {name}")
    if p.parts[0] != root or ".git" in p.parts: fail(f"{name} outside {root}/")

def validate_request(r):
    exact_keys(r,
      {"schema","request_id","repository","base_commit","operation","scope","probe","acknowledgement"},
      {"schema","request_id","repository","base_commit","operation","scope","probe","acknowledgement"})
    if r["schema"] != "rook-link.request.v1": fail("unsupported request schema")
    if not isinstance(r["request_id"], str) or not ID_RE.fullmatch(r["request_id"]): fail("invalid request_id")
    if not isinstance(r["repository"], str) or not REPO_RE.fullmatch(r["repository"]): fail("invalid repository")
    full_sha(r["base_commit"], "base_commit")
    if r["operation"] != "probe.environment.v1": fail("unsupported operation")
    exact_keys(r["scope"], {"mode","allow_mutation","delegate"}, {"mode","allow_mutation","delegate"})
    if r["scope"] != {"mode":"read-only","allow_mutation":False,"delegate":False}: fail("scope must be exactly read-only/non-mutating/non-delegating")
    exact_keys(r["probe"], {"fields","tools"}, {"fields","tools"})
    fields = r["probe"]["fields"]; tools = r["probe"]["tools"]
    if not isinstance(fields,list) or not fields or len(fields)!=len(set(fields)) or not set(fields) <= ALLOWED_PROBES: fail("invalid probe fields")
    if not isinstance(tools,list) or len(tools)!=len(set(tools)) or not set(tools) <= ALLOWED_TOOLS: fail("invalid probe tools")
    if "tool_versions" not in fields and tools: fail("tools require tool_versions field")
    expected = f"rook-link:{r['request_id']}:probe.environment.v1:read-only"
    if r["acknowledgement"] != expected: fail("invalid acknowledgement")

def validate_result(x, req=None):
    exact_keys(x,
      {"schema","request_id","repository","request_commit","request_path","base_commit","operation","status","started_at","finished_at","evidence"},
      {"schema","request_id","repository","request_commit","request_path","base_commit","operation","status","started_at","finished_at","evidence"})
    if x["schema"] != "rook-link.result.v1": fail("unsupported result schema")
    if not isinstance(x["request_id"],str) or not ID_RE.fullmatch(x["request_id"]): fail("invalid request_id")
    if not isinstance(x["repository"],str) or not REPO_RE.fullmatch(x["repository"]): fail("invalid repository")
    full_sha(x["request_commit"], "request_commit"); full_sha(x["base_commit"], "base_commit")
    relpath(x["request_path"], "ops", "request_path")
    if not x["request_path"].startswith("ops/rook/requests/"): fail("request_path must be under ops/rook/requests/")
    if x["operation"] != "probe.environment.v1": fail("unsupported operation")
    if x["status"] not in {"pass","fail","blocked"}: fail("invalid status")
    for k in ("started_at","finished_at"):
        if not isinstance(x[k],str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", x[k]): fail(f"invalid {k}")
    exact_keys(x["evidence"], {"hostname","date_utc","tool_versions","notes"}, set())
    tv = x["evidence"].get("tool_versions", {})
    if not isinstance(tv,dict) or not set(tv) <= ALLOWED_TOOLS or not all(isinstance(v,str) for v in tv.values()): fail("invalid tool_versions evidence")
    if req is not None:
        validate_request(req)
        pairs = [("request_id","request_id"),("repository","repository"),("base_commit","base_commit"),("operation","operation")]
        for rk,qk in pairs:
            if x[rk] != req[qk]: fail(f"result/request mismatch: {rk}")

def load(path):
    with open(path,"r",encoding="utf-8") as f: return json.load(f)

def main():
    p=argparse.ArgumentParser(); p.add_argument("kind",choices=["request","result"]); p.add_argument("file"); p.add_argument("--request")
    a=p.parse_args()
    try:
        obj=load(a.file)
        if a.kind=="request": validate_request(obj); print("valid rook-link request")
        else: validate_result(obj, load(a.request) if a.request else None); print("valid rook-link result")
    except (OSError,json.JSONDecodeError,ValidationError) as e:
        print(f"invalid rook-link {a.kind}: {e}", file=sys.stderr); return 2
    return 0
if __name__ == "__main__": raise SystemExit(main())
