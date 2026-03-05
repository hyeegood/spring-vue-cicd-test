"""
Wikipedia API로 영문 회사명 → 한글 회사명 조회.
"""
import urllib.parse
import urllib.request
import json
from typing import Optional


WIKI_API = "https://en.wikipedia.org/w/api.php"


def fetch_korean_name_from_wikipedia(company_name: str, ticker: str = "") -> Optional[str]:
    """
    영문 회사명으로 위키백과 langlinks API 호출해 한국어 제목 반환.
    company_name: 예 "Apple Inc", ticker: 예 "AAPL" (검색 실패 시 티커로 재시도용)
    """
    if not (company_name or ticker):
        return None
    # 위키 제목: 공백을 밑줄로 (API 규칙)
    search_titles = []
    if company_name:
        search_titles.append(company_name.strip().replace(" ", "_"))
    if ticker and ticker not in (t.replace(" ", "_") for t in search_titles):
        search_titles.append(ticker)

    for title in search_titles:
        if not title:
            continue
        try:
            params = {
                "action": "query",
                "titles": title,
                "prop": "langlinks",
                "lllang": "ko",
                "format": "json",
                "redirects": "1",
            }
            url = f"{WIKI_API}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={"User-Agent": "StockPlatform/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            continue
        try:
            pages = data.get("query", {}).get("pages", {})
            for pid, p in pages.items():
                if pid == "-1":
                    continue
                langlinks = p.get("langlinks", [])
                for ll in langlinks:
                    if ll.get("lang") == "ko":
                        return (ll.get("*") or "").strip() or None
        except Exception:
            continue
    return None
