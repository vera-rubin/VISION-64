from __future__ import annotations

import pytest

from pulse_lite.desktop import conversation_id_from_url, identity_is_exact


def test_conversation_id_from_url_accepts_exact_chat_url():
    assert conversation_id_from_url("https://chatgpt.com/c/abc-123") == "abc-123"


@pytest.mark.parametrize(
    "url",
    [
        "https://chatgpt.com/",
        "https://chatgpt.com/g/g-test",
        "https://chatgpt.com/c/abc/extra",
    ],
)
def test_conversation_id_from_url_rejects_non_chat_routes(url):
    with pytest.raises(ValueError):
        conversation_id_from_url(url)


def test_desktop_identity_accepts_only_strong_current_route_signals():
    assert identity_is_exact(history_state=True, active_anchor=False, selected_container=False)
    assert identity_is_exact(history_state=False, active_anchor=True, selected_container=False)
    assert identity_is_exact(history_state=False, active_anchor=False, selected_container=True)
    assert not identity_is_exact(history_state=False, active_anchor=False, selected_container=False)
