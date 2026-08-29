from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from urllib.parse import urlsplit

from .browser import BrowserState, validate_cdp_url, validate_conversation_url


def conversation_id_from_url(url: str) -> str:
    validate_conversation_url(url)
    parts = [part for part in urlsplit(url).path.split("/") if part]
    if len(parts) != 2 or parts[0] != "c" or not parts[1]:
        raise ValueError("desktop mode requires an exact https://chatgpt.com/c/<conversation-id> URL")
    return parts[1]


def identity_is_exact(*, history_state: bool, active_anchor: bool, selected_container: bool) -> bool:
    # Only current-route/selection signals are authoritative. Mere presence in DOM, storage,
    # sidebar history, or resource history can refer to an inactive conversation.
    return history_state or active_anchor or selected_container


@dataclass(slots=True)
class DesktopIdentity:
    exact: bool
    history_state: bool
    active_anchor: bool
    selected_container: bool
    matching_anchor_count: int
    visible_matching_anchor_count: int
    dom_contains_id: bool
    local_storage_contains_id: bool
    session_storage_contains_id: bool
    resource_url_contains_id: bool

    def public_dict(self) -> dict[str, bool | int]:
        return {
            "exact": self.exact,
            "history_state": self.history_state,
            "active_anchor": self.active_anchor,
            "selected_container": self.selected_container,
            "matching_anchor_count": self.matching_anchor_count,
            "visible_matching_anchor_count": self.visible_matching_anchor_count,
            "dom_contains_id": self.dom_contains_id,
            "local_storage_contains_id": self.local_storage_contains_id,
            "session_storage_contains_id": self.session_storage_contains_id,
            "resource_url_contains_id": self.resource_url_contains_id,
        }


class DesktopChatGPTAdapter:
    """Fail-closed adapter for the ChatGPT Windows desktop Chromium renderer.

    ChatGPT desktop exposes an app:/// page rather than the public conversation URL. PULSE must
    separately prove that the configured conversation is the active desktop conversation before
    it will inject, stop generation, or reload.
    """

    MAIN_PAGE_URL = "app:///-/index.html"

    def __init__(self, cdp_url: str, conversation_url: str) -> None:
        validate_cdp_url(cdp_url)
        self.cdp_url = cdp_url
        self.conversation_url = conversation_url
        self.conversation_id = conversation_id_from_url(conversation_url)

    def _with_page(self):
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("playwright is not installed") from exc

        pw = sync_playwright().start()
        try:
            browser = pw.chromium.connect_over_cdp(self.cdp_url)
            matches = [
                page
                for context in browser.contexts
                for page in context.pages
                if page.url == self.MAIN_PAGE_URL
            ]
            if len(matches) != 1:
                pw.stop()
                raise RuntimeError(
                    f"expected exactly one ChatGPT desktop main renderer, found {len(matches)}"
                )
            return pw, matches[0]
        except Exception:
            try:
                pw.stop()
            except Exception:
                pass
            raise

    @staticmethod
    def _composer(page):
        boxes = page.get_by_role("textbox", name="Message ChatGPT")
        visible = []
        try:
            for i in range(boxes.count()):
                box = boxes.nth(i)
                if box.is_visible():
                    visible.append(box)
        except Exception:
            return None
        return visible[0] if len(visible) == 1 else None

    @staticmethod
    def _composer_text(composer) -> str | None:
        try:
            return composer.inner_text(timeout=1000)
        except Exception:
            try:
                return composer.input_value(timeout=1000)
            except Exception:
                return None

    @staticmethod
    def _stop_button(page):
        for selector in (
            'button[data-testid="stop-button"]',
            'button[aria-label="Stop streaming"]',
            'button[aria-label="Stop generating"]',
        ):
            loc = page.locator(selector)
            try:
                if loc.count() == 1 and loc.is_visible():
                    return loc
            except Exception:
                continue
        return None

    @classmethod
    def _is_generating(cls, page) -> bool:
        return cls._stop_button(page) is not None

    @staticmethod
    def _send_button(page):
        for selector in (
            'button[data-testid="send-button"]',
            'button[aria-label="Send message"]',
            'button[aria-label="Send prompt"]',
        ):
            loc = page.locator(selector)
            try:
                if loc.count() == 1 and loc.is_visible() and loc.is_enabled():
                    return loc
            except Exception:
                continue
        return None

    @staticmethod
    def _progress_signature(page) -> str | None:
        try:
            main = page.locator("main")
            if main.count() != 1:
                return None
            text = main.inner_text(timeout=1500)
            return sha256(text[-4000:].encode("utf-8", errors="ignore")).hexdigest()
        except Exception:
            return None

    def _identity(self, page) -> DesktopIdentity:
        raw = page.evaluate(
            """cid => {
                const contains = value => {
                    try { return JSON.stringify(value).includes(cid); }
                    catch { return false; }
                };
                const matching = Array.from(document.querySelectorAll("a[href]"))
                    .filter(a => (a.getAttribute("href") || "").includes(cid));
                const visible = matching.filter(a => {
                    const r = a.getBoundingClientRect();
                    const s = getComputedStyle(a);
                    return r.width > 0 && r.height > 0
                        && s.visibility !== "hidden" && s.display !== "none";
                });
                const selected = el => {
                    if (!el) return false;
                    const ac = (el.getAttribute("aria-current") || "").toLowerCase();
                    const as = (el.getAttribute("aria-selected") || "").toLowerCase();
                    const ds = (el.getAttribute("data-state") || "").toLowerCase();
                    const dsel = (el.getAttribute("data-selected") || "").toLowerCase();
                    return ["page", "true", "active", "selected"].includes(ac)
                        || as === "true"
                        || ["active", "selected", "open", "current"].includes(ds)
                        || dsel === "true";
                };
                const activeAnchor = matching.some(a => selected(a));
                const selectedContainer = matching.some(a => {
                    let node = a.parentElement;
                    for (let depth = 0; node && depth < 6; depth++, node = node.parentElement) {
                        if (selected(node)) return true;
                    }
                    return false;
                });

                let local = false;
                let session = false;
                try {
                    for (let i = 0; i < localStorage.length; i++) {
                        const k = localStorage.key(i);
                        if ((k && k.includes(cid)) || (localStorage.getItem(k) || "").includes(cid)) {
                            local = true;
                            break;
                        }
                    }
                } catch {}
                try {
                    for (let i = 0; i < sessionStorage.length; i++) {
                        const k = sessionStorage.key(i);
                        if ((k && k.includes(cid)) || (sessionStorage.getItem(k) || "").includes(cid)) {
                            session = true;
                            break;
                        }
                    }
                } catch {}

                return {
                    history_state: contains(history.state),
                    active_anchor: activeAnchor,
                    selected_container: selectedContainer,
                    matching_anchor_count: matching.length,
                    visible_matching_anchor_count: visible.length,
                    dom_contains_id: document.documentElement.outerHTML.includes(cid),
                    local_storage_contains_id: local,
                    session_storage_contains_id: session,
                    resource_url_contains_id: performance.getEntriesByType("resource")
                        .some(e => (e.name || "").includes(cid))
                };
            }""",
            self.conversation_id,
        )
        exact = identity_is_exact(
            history_state=bool(raw["history_state"]),
            active_anchor=bool(raw["active_anchor"]),
            selected_container=bool(raw["selected_container"]),
        )
        return DesktopIdentity(exact=exact, **raw)

    def identity_diagnostics(self) -> dict[str, bool | int | str]:
        pw = None
        try:
            pw, page = self._with_page()
            return {"page_url": page.url, **self._identity(page).public_dict()}
        finally:
            if pw is not None:
                pw.stop()

    def inspect(self) -> BrowserState:
        pw = None
        try:
            pw, page = self._with_page()
            identity = self._identity(page)
            composer = self._composer(page)
            generating = self._is_generating(page)
            signature = self._progress_signature(page)
            if not identity.exact:
                return BrowserState(
                    False,
                    composer is not None,
                    False,
                    generating,
                    signature,
                    "desktop conversation identity not proven",
                )
            if composer is None:
                return BrowserState(
                    True, False, False, generating, signature,
                    "composer not confidently identified",
                )
            text = self._composer_text(composer)
            if text is None:
                return BrowserState(True, True, False, generating, signature, "composer text unreadable")
            return BrowserState(True, True, text.strip() == "", generating, signature, "ok")
        finally:
            if pw is not None:
                pw.stop()

    def inject(self, prompt: str) -> tuple[bool, str]:
        if not prompt.strip():
            return False, "empty prompt"
        pw = None
        try:
            pw, page = self._with_page()
            if not self._identity(page).exact:
                return False, "desktop conversation identity not proven"
            if self._is_generating(page):
                return False, "page is generating"
            composer = self._composer(page)
            if composer is None:
                return False, "composer not confidently identified"
            existing = self._composer_text(composer)
            if existing is None:
                return False, "composer text unreadable"
            if existing.strip():
                return False, "composer occupied by user text"
            try:
                composer.fill(prompt)
            except Exception:
                try:
                    composer.click()
                    page.keyboard.insert_text(prompt)
                except Exception as exc:
                    return False, f"composer write failed: {type(exc).__name__}"
            observed = self._composer_text(composer)
            if observed is None or observed.strip() != prompt.strip():
                try:
                    composer.fill("")
                except Exception:
                    pass
                return False, "composer write could not be verified"
            send = self._send_button(page)
            if send is None:
                try:
                    composer.fill("")
                except Exception:
                    pass
                return False, "send button not confidently available"
            send.click()
            return True, "submitted"
        finally:
            if pw is not None:
                pw.stop()

    def stop_generation(self) -> tuple[bool, str]:
        pw = None
        try:
            pw, page = self._with_page()
            if not self._identity(page).exact:
                return False, "desktop conversation identity not proven"
            button = self._stop_button(page)
            if button is None:
                return False, "stop control not confidently available"
            try:
                button.click(timeout=2000)
                return True, "stop requested"
            except Exception as exc:
                return False, f"stop click failed: {type(exc).__name__}"
        finally:
            if pw is not None:
                pw.stop()

    def reload_exact_conversation(self) -> tuple[bool, str]:
        pw = None
        try:
            pw, page = self._with_page()
            if not self._identity(page).exact:
                return False, "desktop conversation identity not proven"
            page.reload(wait_until="domcontentloaded", timeout=30000)
            if page.url != self.MAIN_PAGE_URL:
                return False, "desktop reload navigated away from main renderer"
            if not self._identity(page).exact:
                return False, "desktop conversation identity lost after reload"
            return True, "reloaded"
        except Exception as exc:
            return False, f"reload failed: {type(exc).__name__}"
        finally:
            if pw is not None:
                pw.stop()
