"""Scrape grant/charity pages and write cleaned text under textfiles/."""

from pathlib import Path

import requests
from bs4 import BeautifulSoup, Comment

TEXTFILES_DIR = Path("./textfiles")
MIN_WORDS = 40
REQUEST_TIMEOUT = 30
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
BOILERPLATE_TAGS = {
    "script",
    "style",
    "noscript",
    "template",
    "iframe",
    "svg",
    "canvas",
    "nav",
    "footer",
    "header",
    "aside",
}
NOISE_KEYWORDS = (
    "cookie",
    "consent",
    "gdpr",
    "banner",
    "popup",
    "modal",
    "newsletter",
    "subscribe",
    "social",
    "share",
    "breadcrumb",
    "menu",
    "nav",
)


def scrape_charity_website(url, text_filename):
    """Download a page, extract main text, and save it to textfiles/<name>.txt."""
    html = _fetch_html(url)
    cleaned = extract_main_text(html)
    if _word_count(cleaned) < MIN_WORDS:
        rendered = _fetch_html_with_playwright(url)
        if rendered:
            cleaned = extract_main_text(rendered)
    if _word_count(cleaned) < MIN_WORDS:
        raise RuntimeError(
            "Not enough readable text on this page. It may be JavaScript-only or blocked. "
            "Install Playwright browsers with: pip install playwright && playwright install chromium"
        )

    TEXTFILES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TEXTFILES_DIR / f"{text_filename}.txt"
    output_path.write_text(cleaned, encoding="utf-8")
    return cleaned


def extract_main_text(html):
    """Keep article/main copy and drop navigation, chrome, and cookie UI."""
    soup = BeautifulSoup(html, "html.parser")
    for comment in soup.find_all(string=lambda node: isinstance(node, Comment)):
        comment.extract()
    for tag in soup.find_all(BOILERPLATE_TAGS):
        tag.decompose()
    for tag in soup.find_all(True):
        marker = " ".join(
            filter(
                None,
                [
                    " ".join(tag.get("class", [])),
                    tag.get("id") or "",
                    tag.get("role") or "",
                    tag.get("aria-label") or "",
                ],
            )
        ).lower()
        if any(keyword in marker for keyword in NOISE_KEYWORDS):
            tag.decompose()

    root = (
        soup.find("main")
        or soup.find("article")
        or soup.find(attrs={"role": "main"})
        or soup.find("body")
        or soup
    )
    lines = [line.strip() for line in root.get_text(separator="\n").splitlines() if line.strip()]
    return "\n".join(lines)


def _fetch_html(url):
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.text


def _fetch_html_with_playwright(url):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT)
            page.goto(url, wait_until="networkidle", timeout=REQUEST_TIMEOUT * 1000)
            html = page.content()
            browser.close()
            return html
    except Exception as exc:
        print(f"Playwright fallback failed: {exc}")
        return None


def _word_count(text):
    return len(text.split())
