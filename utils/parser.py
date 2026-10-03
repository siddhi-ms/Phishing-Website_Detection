"""URL parsing helpers (string processing only - no network access)."""
import ipaddress
from urllib.parse import urlsplit

# Hash set of common two-part public suffixes (so 'bbc.co.uk' has domain 'bbc.co.uk')
MULTI_PART_SUFFIXES = {
    "co.uk", "org.uk", "ac.uk", "gov.uk", "com.au", "net.au", "org.au", "co.in", "net.in",
    "org.in", "ac.in", "gov.in", "co.jp", "com.br", "com.cn", "co.za", "co.nz", "com.mx",
    "com.sg", "com.tr",
}


def normalize_url(raw):
    """Strip spaces; if no scheme is given assume http://. Returns (url, scheme_assumed)."""
    url = raw.strip()
    if "://" not in url:
        return "http://" + url, True
    return url, False


def is_ip_address(host):
    try:
        ipaddress.ip_address(host.strip("[]"))
        return True
    except ValueError:
        return False


def validate_url(raw):
    """Return an error message, or None when the URL looks usable."""
    raw = (raw or "").strip()
    if not raw:
        return "Please enter a URL, for example https://example.com"
    if any(ch.isspace() for ch in raw):
        return "The URL must not contain spaces."
    if len(raw) > 2000:
        return "The URL is too long (limit 2000 characters)."
    url, _ = normalize_url(raw)
    try:
        parts = urlsplit(url)
        host = parts.hostname
        _ = parts.port
    except ValueError:
        return "This does not look like a valid URL."
    if parts.scheme not in ("http", "https"):
        return "Only http:// and https:// URLs are supported."
    if not host:
        return "Could not find a domain name in this URL."
    if not is_ip_address(host):
        labels = host.split(".")
        if len(labels) < 2 or any(not label for label in labels):
            return "The domain looks incomplete. Use a full domain such as example.com"
    return None


def parse_url(url):
    """Split a normalised URL into protocol, domain, subdomain, path, ... (dict)."""
    parts = urlsplit(url)
    host = parts.hostname or ""
    ip = is_ip_address(host)
    subdomain, suffix, domain = "", "", host
    if not ip and host:
        labels = host.split(".")
        n_suffix = 2 if len(labels) >= 3 and ".".join(labels[-2:]) in MULTI_PART_SUFFIXES else 1
        n_suffix = min(n_suffix, max(len(labels) - 1, 0))
        suffix = ".".join(labels[-n_suffix:]) if n_suffix else ""
        domain = ".".join(labels[-(n_suffix + 1):])
        subdomain = ".".join(labels[:-(n_suffix + 1)])
    return {
        "url": url,
        "scheme": parts.scheme,
        "hostname": host,
        "is_ip": ip,
        "subdomain": subdomain,
        "domain": domain,
        "suffix": suffix,
        "path": parts.path,
        "query": parts.query,
        "port": parts.port,
    }
