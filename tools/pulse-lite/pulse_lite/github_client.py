from __future__ import annotations

from dataclasses import dataclass
import json
import re
import subprocess
from typing import Any

from .state import WakeEvent

REQUEST_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")


class GhError(RuntimeError):
    pass


@dataclass(slots=True)
class GhClient:
    executable: str = "gh"

    def _run(self, args: list[str]) -> str:
        proc = subprocess.run(
            [self.executable, *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            message = (proc.stderr or proc.stdout).strip()
            raise GhError(message or f"gh exited {proc.returncode}")
        return proc.stdout

    def auth_ok(self) -> bool:
        try:
            self._run(["auth", "status"])
        except GhError:
            return False
        return True

    def can_read_repo(self, repository: str) -> bool:
        try:
            self._run(["api", f"repos/{repository}", "--jq", ".full_name"])
        except GhError:
            return False
        return True

    def issue_comments(self, repository: str, issue: int) -> list[dict[str, Any]]:
        out = self._run(
            [
                "api",
                f"repos/{repository}/issues/{issue}/comments",
                "--paginate",
                "--slurp",
            ]
        )
        pages = json.loads(out)
        if not isinstance(pages, list):
            raise GhError("unexpected gh comments response")
        flattened: list[dict[str, Any]] = []
        for page in pages:
            if isinstance(page, list):
                flattened.extend(item for item in page if isinstance(item, dict))
        return flattened

    def matching_events(
        self,
        repository: str,
        issue: int,
        request_prefix: str,
        *,
        after_comment_id: int = 0,
    ) -> list[WakeEvent]:
        events: list[WakeEvent] = []
        for comment in self.issue_comments(repository, issue):
            comment_id = comment.get("id")
            body = comment.get("body")
            if not isinstance(comment_id, int) or comment_id <= after_comment_id:
                continue
            if not isinstance(body, str):
                continue
            try:
                envelope = json.loads(body)
            except json.JSONDecodeError:
                continue
            if not isinstance(envelope, dict):
                continue
            schema = envelope.get("schema")
            if schema not in {"rook-link.result.v1", "rook-link.result.v2"}:
                continue
            request_id = envelope.get("request_id")
            if not isinstance(request_id, str) or not REQUEST_ID_RE.fullmatch(request_id):
                continue
            if not request_id.startswith(request_prefix):
                continue
            request_commit = envelope.get("request_commit")
            request_path = envelope.get("request_path")
            if request_commit is not None and (
                not isinstance(request_commit, str) or not FULL_SHA_RE.fullmatch(request_commit)
            ):
                continue
            if request_path is not None and (
                not isinstance(request_path, str)
                or not request_path.startswith("ops/rook/requests/")
                or ".." in request_path.split("/")
                or "\\" in request_path
            ):
                continue
            events.append(
                WakeEvent(
                    comment_id=comment_id,
                    request_id=request_id,
                    schema=schema,
                    request_commit=request_commit,
                    request_path=request_path,
                )
            )
        events.sort(key=lambda e: e.comment_id)
        return events

    def redeliver(
        self,
        *,
        repository: str,
        workflow: str,
        ref: str,
        request_id: str,
        request_commit: str,
        request_path: str,
    ) -> None:
        if not FULL_SHA_RE.fullmatch(request_commit):
            raise GhError("request_commit must be a full lowercase commit SHA")
        if not request_path.startswith("ops/rook/requests/") or ".." in request_path.split("/"):
            raise GhError("request_path must stay under ops/rook/requests/")
        if not REQUEST_ID_RE.fullmatch(request_id):
            raise GhError("invalid request_id")
        self._run(
            [
                "workflow",
                "run",
                workflow,
                "--repo",
                repository,
                "--ref",
                ref,
                "-f",
                f"request_id={request_id}",
                "-f",
                f"request_commit={request_commit}",
                "-f",
                f"request_path={request_path}",
            ]
        )
