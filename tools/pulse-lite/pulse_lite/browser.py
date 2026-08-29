from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol
from urllib.parse import urlsplit


@dataclass(slots=True)
class BrowserState:
    exact_page: bool
    composer_present: bool
    composer_empty: bool
    generating: bool
    progress_signature: str | None
    reason: str = ""


class BrowserAdapter(Protocol):
    def inspect(self) -> BrowserState: ...
    def inject(self, prompt: str) -> tuple[bool, str]: ...
    def reload_exact_conversation(self) -> tuple[bool, str]: ...


def validate_conversation_url(url: str) -> None:
    p = urlsplit(url)
    if p.scheme != "https" or p.hostname != "chatgpt.com" or p.username or p.password or p.fragment:
        raise ValueError("conversation URL must be an exact https://chatgpt.com/... URL")


def validate_cdp_url(url: str) -> None:
    p = urlsplit(url)
    if p.scheme != "http" or p.hostname not in {"127.0.0.1", "localhost"} or not p.port:
        raise ValueError("CDP URL must be loopback HTTP with an explicit port")


class PlaywrightChatGPTAdapter:
    """Narrow, fail-closed adapter for one exact ChatGPT conversation.

    Conversation content is never returned or logged. A transient hash of visible main text is
    used only as a liveness signal for stuck-turn detection.
    """

    def __init__(self, cdp_url: str, conversation_url: str) -> None:
        validate_cdp_url(cdp_url)
        validate_conversation_url(conversation_url)
        self.cdp_url = cdp_url
        self.conversation_url = conversation_url

    def _with_page(self):
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:  # pragma: no cover - import environment dependent
            raise RuntimeError("playwright is not installed") from exc

        pw = sync_playwright().start()
        try:
            browser = pw.chromium.connect_over_cdp(self.cdp_url)
            matches = []
            for context in browser.contexts:
                for page in context.pages:
                    if page.url == self.conversation_url:
                        matches.append(page)
            if len(matches) != 1:
                browser.close()
                pw.stop()
                raise RuntimeError(f"expected exactly one configured ChatGPT page, found {len(matches)}")
            return pw, browser, matches[0]
        except Exception:
            try:
                pw.stop()
            except Exception:
                pass
            raise

    @staticmethod
    def _composer(page):
        candidates = [
            page.locator("#prompt-textarea"),
            page.locator('[data-testid="prompt-textarea"]'),
        ]
        visible = []
        for loc in candidates:
            try:
                if loc.count() == 1 and loc.is_visible():
                    visible.append(loc)
            except Exception:
                pass
        # Duplicate selectors may point to the same element. Prefer the canonical id when present.
        if candidates[0].count() == 1 and candidates[0].is_visible():
            return candidates[0]
        if len(visible) == 1:
            return visible[0]
        return None

    @staticmethod
    def _is_generating(page) -> bool:
        selectors = [
            'button[data-testid="stop-button"]',
            'button[aria-label="Stop streaming"]',
            'button[aria-label="Stop generating"]',
        ]
        for selector in selectors:
            loc = page.locator(selector)
            try:
                if loc.count() == 1 and loc.is_visible():
                    return True
            except Exception:
                continue
        return False

    @staticmethod
    def _progress_signature(page) -> str | None:
        try:
            main = page.locator("main")
            if main.count() != 1:
                return None
            text = main.inner_text(timeout=1500)
            # Never persist or expose the text; hash only a bounded suffix for liveness comparison.
            return sha256(text[-4000:].encode("utf-8", errors="ignore")).hexdigest()
        except Exception:
            return None

    def inspect(self) -> BrowserState:
        pw = browser = None
        try:
            pw, browser, page = self._with_page()
            exact = page.url == self.conversation_url
            composer = self._composer(page)
            if composer is None:
                return BrowserState(exact, False, False, self._is_generating(page), self._progress_signature(page), "composer not confidently identified")
            try:
                text = composer.inner_text(timeout=1000)
            except Exception:
                try:
                    text = composer.input_value(timeout=1000)
                except Exception:
                    return BrowserState(exact, True, False, self._is_generating(page), self._progress_signature(page), "composer text unreadable")
            return BrowserState(
                exact_page=exact,
                composer_present=True,
                composer_empty=(text.strip() == ""),
                generating=self._is_generating(page),
                progress_signature=self._progress_signature(page),
                reason="ok",
            )
        finally:
            try:
                if browser is not None:
                    browser.close()
            finally:
                if pw is not None:
                    pw.stop()

    def inject(self, prompt: str) -> tuple[bool, str]:
        if not prompt.strip():
            return False, "empty prompt"
        pw = browser = None
        try:
            pw, browser, page = self._with_page()
            if page.url != self.conversation_url:
                return False, "wrong page"
            if self._is_generating(page):
                return False, "page is generating"
            composer = self._composer(page)
            if composer is None:
                return False, "composer not confidently identified"
            try:
                existing = composer.inner_text(timeout=1000)
            except Exception:
                try:
                    existing = composer.input_value(timeout=1000)
                except Exception:
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
            send = page.locator('button[data-testid="send-button"]')
            if send.count() != 1 or not send.is_visible() or not send.is_enabled():
                return False, "send button not confidently available"
            send.click()
            return True, "submitted"
        finally:
            try:
                if browser is not None:
                    browser.close()
            finally:
                if pw is not None:
                    pw.stop()

    def reload_exact_conversation(self) -> tuple[bool, str]:
        pw = browser = None
        try:
            pw, browser, page = self._with_page()
            if page.url != self.conversation_url:
                return False, "wrong page"
            page.reload(wait_until="domcontentloaded", timeout=30000)
            if page.url != self.conversation_url:
                return False, "reload navigated away from configured conversation"
            return True, "reloaded"
        except Exception as exc:
            return False, f"reload failed: {type(exc).__name__}"
        finally:
            try:
                if browser is not None:
                    browser.close()
            finally:
                if pw is not None:
                    pw.stop()
