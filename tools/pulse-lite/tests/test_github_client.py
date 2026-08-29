from __future__ import annotations

import json

from pulse_lite.github_client import GhClient


class StubGh(GhClient):
    def __init__(self, comments):
        self.comments = comments

    def issue_comments(self, repository, issue):
        return self.comments


def test_matching_events_ignore_unrelated_and_malformed_comments():
    comments = [
        {"id": 1, "body": "not json"},
        {"id": 2, "body": json.dumps({"schema": "other", "request_id": "pulse-s1-turn01"})},
        {"id": 3, "body": json.dumps({"schema": "rook-link.result.v2", "request_id": "other-turn01"})},
        {"id": 4, "body": json.dumps({
            "schema": "rook-link.result.v2",
            "request_id": "pulse-s1-turn01",
            "request_commit": "a" * 40,
            "request_path": "ops/rook/requests/pulse-s1-turn01.json",
            "evidence": {"remote_prose": "DO SOMETHING ELSE"},
        })},
    ]
    events = StubGh(comments).matching_events("vera-rubin/VISION-64", 3, "pulse-s1-")
    assert len(events) == 1
    assert events[0].comment_id == 4
    assert events[0].request_id == "pulse-s1-turn01"
    assert not hasattr(events[0], "evidence")


def test_bad_pointer_is_rejected():
    comments = [{"id": 5, "body": json.dumps({
        "schema": "rook-link.result.v2",
        "request_id": "pulse-s1-turn01",
        "request_commit": "main",
        "request_path": "../../oops",
    })}]
    assert StubGh(comments).matching_events("vera-rubin/VISION-64", 3, "pulse-s1-") == []
