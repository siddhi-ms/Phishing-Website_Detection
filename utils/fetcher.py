"""Fetch a live web page and compute the ONE feature that needs page content
(PctExtHyperlinks). Everything else still comes from the URL text alone.

This makes a real outbound HTTP request to the URL the user typed. Only
downloads the HTML (never executes scripts, never follows the page's own
redirects into a browser) and is capped on size, time and redirects.
"""
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup

USER_AGENT = "PhishGuardAI-Scanner/1.0 (+educational project; feature extraction only)"
TIMEOUT = 6                # seconds
MAX_BYTES = 2_000_000      # stop downloading after ~2 MB
MAX_REDIRECTS = 5


class FetchError(Exception):
    """Raised when the page cannot be safely retrieved or parsed."""


def _registrable_domain(hostname):
    """Best-effort 'last two labels' comparison (same approach as utils/parser.py)."""
    labels = (hostname or "").lower().split(".")
    return ".".join(labels[-2:]) if len(labels) >= 2 else hostname or ""


def fetch_html(url):
    """Download the page and return decoded HTML text, with a hard size cap."""
    try:
        resp = requests.get(
            url, timeout=TIMEOUT, allow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"},
            stream=True,
        )
    except requests.exceptions.SSLError as exc:
        raise FetchError("The site's HTTPS certificate could not be verified.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise FetchError("Could not connect to this host (DNS failure, refused, or offline).") from exc
    except requests.exceptions.Timeout as exc:
        raise FetchError(f"The site did not respond within {TIMEOUT} seconds.") from exc
    except requests.exceptions.TooManyRedirects as exc:
        raise FetchError("Too many redirects.") from exc
    except requests.exceptions.RequestException as exc:
        raise FetchError(f"Request failed: {exc}") from exc

    if len(resp.history) > MAX_REDIRECTS:
        resp.close()
        raise FetchError("Too many redirects.")
    if resp.status_code >= 400:
        resp.close()
        raise FetchError(f"The server returned HTTP {resp.status_code}.")

    ctype = resp.headers.get("Content-Type", "")
    if "text/html" not in ctype and "application/xhtml" not in ctype and ctype != "":
        resp.close()
        raise FetchError(f"Page is not HTML (Content-Type: {ctype}).")

    chunks, total = [], 0
    for chunk in resp.iter_content(chunk_size=8192, decode_unicode=False):
        total += len(chunk)
        chunks.append(chunk)
        if total > MAX_BYTES:
            break
    resp.close()
    raw = b"".join(chunks)
    return raw.decode(resp.encoding or "utf-8", errors="replace"), resp.url


def external_link_ratio(html, final_url):
    """Fraction of <a href> links that point to a different registrable domain."""
    soup = BeautifulSoup(html, "html.parser")
    page_domain = _registrable_domain(urlsplit(final_url).hostname)

    total = external = 0
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        total += 1
        absolute = urljoin(final_url, href)
        link_domain = _registrable_domain(urlsplit(absolute).hostname)
        if link_domain and link_domain != page_domain:
            external += 1

    if total == 0:
        return 0.0, 0, 0
    return round(external / total, 4), external, total


def analyze_live_page(url):
    """Fetch the page and return (pct_external, external_count, total_count, final_url)."""
    html, final_url = fetch_html(url)
    pct, external, total = external_link_ratio(html, final_url)
    return pct, external, total, final_url
