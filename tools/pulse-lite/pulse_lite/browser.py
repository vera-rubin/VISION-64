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
    def stop_generation(self) -> tuple[bool, str]: ...
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
    """Fail-closed adapter for one exact ChatGPT conversation.

    It never reads conversation text as authority. A transient hash of a bounded visible suffix is
    used only as a local liveness signal. The hash is not persisted outside SessionState.
    """

    def __init__(self, cdp_url: str, conversation_url: str) -> None:
        validate_cdp_url(cdp_url)
        validate_conversation_url(conversation_url)
        self.cdp_url = cdp_url
        self.conversation_url = conversation_url

    def _with_page(self):
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:  # pragma: no cover
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
                pw.stop()
                raise RuntimeError(f"expected exactly one configured ChatGPT page, found {len(matches)}")
            return pw, matches[0]
        except Exception:
            try:
                pw.stop()
            except Exception:
                pass
            raise

    @staticmethod
    def _composer(page):
        canonical = page.locator("#prompt-textarea")
        try:
            if canonical.count() == 1 and canonical.is_visible():
                return canonical
        except Exception:
            pass
        fallback = page.locator('[data-testid="prompt-textarea"]')
        try:
            if fallback.count() == 1 and fallback.is_visible():
                return fallback
        except Exception:
            pass
        return None

    @staticmethod
    def _stop_button(page):
        selectors = [
            'button[data-testid="stop-button"]',
            'button[aria-label="Stop streaming"]',
            'button[aria-label="Stop generating"]',
        ]
        visible = []
        for selector in selectors:
            loc = page.locator(selector)
            try:
                if loc.count() == 1 and loc.is_visible():
                    visible.append(loc)
            except Exception:
                continue
        # Multiple selector forms can point to the same DOM element. De-duplicate by element handle.
        unique = []
        seen = set()
        for loc in visible:
            try:
                handle = loc.element_handle(timeout=500)
                key = id(handle) if handle is not None else None
            except Exception:
                key = None
            if key is None or key not in seen:
                unique.append(loc)
                if key is not None:
                    seen.add(key)
        if len(unique) == 1:
            return unique[0]
        if visible:
            # Prefer the canonical data-testid only when it is singular and visible.
            canonical = page.locator('button[data-testid="stop-button"]')
            try:
                if canonical.count() == 1 and canonical.is_visible():
                    return canonical
            except Exception:
                pass
        return None

    @classmethod
    def _is_generating(cls, page) -> bool:
        return cls._stop_button(page) is not None

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

    @staticmethod
    def _composer_text(composer) -> str | None:
        try:
            return composer.inner_text(timeout=1000)
        except Exception:
            try:
                return composer.input_value(timeout=1000)
            except Exception:
                return None

    def inspect(self) -> BrowserState:
        pw = None
        try:
            pw, page = self._with_page()
            exact = page.url == self.conversation_url
            composer = self._composer(page)
            generating = self._is_generating(page)
            signature = self._progress_signature(page)
            if composer is None:
                return BrowserState(exact, False, False, generating, signature, "composer not confidently identified")
            text = self._composer_text(composer)
            if text is None:
                return BrowserState(exact, True, False, generating, signature, "composer text unreadable")
            return BrowserState(exact, True, text.strip() == "", generating, signature, "ok")
        finally:
            if pw is not None:
                pw.stop()

    def inject(self, prompt: str) -> tuple[bool, str]:
        if not prompt.strip():
            return False, "empty prompt"
        pw = None
        try:
            pw, page = self._with_page()
            if page.url != self.conversation_url:
                return False, "wrong page"
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
            send = page.locator('button[data-testid="send-button"]')
            if send.count() != 1 or not send.is_visible() or not send.is_enabled():
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
            if page.url != self.conversation_url:
                return False, "wrong page"
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
            if page.url != self.conversation_url:
                return False, "wrong page"
            page.reload(wait_until="domcontentloaded", timeout=30000)
            if page.url != self.conversation_url:
                return False, "reload navigated away from configured conversation"
            return True, "reloaded"
        except Exception as exc:
            return False, f"reload failed: {type(exc).__name__}"
        finally:
            if pw is not None:
                pw.stop()
