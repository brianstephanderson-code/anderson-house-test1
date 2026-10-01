#!/data/data/com.termux/files/usr/bin/python
"""Small deterministic provenance classifier for 3 Amigos.
Classifies source lanes without substring-spoofing hostnames.
No network and no credentials required.
"""
from urllib.parse import urlparse

END_USER_DOMAINS=("reddit.com","stackexchange.com","stackoverflow.com")


def _host(url):
    return (urlparse(str(url)).hostname or "").lower().rstrip(".")


def _is_or_subdomain(host, domain):
    return host == domain or host.endswith("." + domain)


def classify_source(url):
    host=_host(url)
    if not host:
        return "other"
    # Boundary-aware institutional suffixes. Do not use loose '.gov' substring tests:
    # evil.gov.example.com must never become official evidence.
    if host.endswith((".gov", ".gov.au", ".edu", ".edu.au")):
        return "official"
    if any(_is_or_subdomain(host,d) for d in END_USER_DOMAINS):
        return "end_user"
    # Forum/community labels are useful discovery hints, but are not sufficient
    # provenance by themselves to certify an end-user lane.
    return "other"


def self_test():
    cases={
        "https://www.wa.gov.au/rules":"official",
        "https://fisheries.gov.au/info":"official",
        "https://example.edu/paper":"official",
        "https://evil.gov.example.com/fake":"other",
        "https://docs.example.com/page":"other",
        "https://reddit.com/r/fishing/x":"end_user",
        "https://old.reddit.com/r/fishing/x":"end_user",
        "https://notreddit.com/post":"other",
        "file:///tmp/x":"other",
    }
    for url,want in cases.items():
        got=classify_source(url)
        assert got==want,(url,got,want)
    return True

if __name__=="__main__":
    self_test()
    print("PASS: source provenance classifier")
