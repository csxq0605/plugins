"""Search engine — arXiv and Semantic Scholar API integration.

Provides programmatic search for academic papers via official APIs.
No API key required for basic usage (Semantic Scholar rate-limited without key).
"""

import json
import os
import ssl
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# Allow unverified SSL for environments without proper cert store
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


# ---------------------------------------------------------------------------
# Config management — unified for Claude Code and Nexgent
# ---------------------------------------------------------------------------

_CONFIG_DIR = Path.home() / ".lit-review"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def _load_config() -> dict:
    """Load config from ~/.lit-review/config.json."""
    if _CONFIG_FILE.exists():
        try:
            with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_config(config: dict):
    """Save config to ~/.lit-review/config.json."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_api_key() -> str:
    """Get Semantic Scholar API key from (in priority order):
    1. Environment variable SEMANTIC_SCHOLAR_API_KEY
    2. Config file ~/.lit-review/config.json
    """
    env_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    if env_key:
        return env_key
    config = _load_config()
    return config.get("semantic_scholar_api_key", "")


def set_api_key(key: str) -> dict:
    """Save Semantic Scholar API key to config file."""
    config = _load_config()
    config["semantic_scholar_api_key"] = key
    _save_config(config)
    return {"status": "ok", "message": f"API key saved to {_CONFIG_FILE}"}


def get_config() -> dict:
    """Get current config."""
    config = _load_config()
    return {
        "config_file": str(_CONFIG_FILE),
        "semantic_scholar_api_key": "***" + get_api_key()[-4:] if get_api_key() else "(not set)",
        "env_key_set": bool(os.environ.get("SEMANTIC_SCHOLAR_API_KEY")),
    }


# ---------------------------------------------------------------------------
# arXiv API
# ---------------------------------------------------------------------------

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
_last_arxiv_call = 0.0


def search_arxiv(query: str, max_results: int = 10, sort_by: str = "relevance",
                 sort_order: str = "descending", categories: str = "",
                 date_from: str = "", date_to: str = "") -> dict:
    """Search arXiv API.

    Args:
        query: Search query (supports arXiv field prefixes: ti, au, abs, cat, all)
        max_results: Max results (default 10, max 100)
        sort_by: relevance, lastUpdatedDate, submittedDate
        sort_order: ascending, descending
        categories: Comma-separated arXiv categories (e.g. cs.AI,cs.LG)
        date_from: Start date YYYY-MM-DD
        date_to: End date YYYY-MM-DD

    Returns:
        dict with papers list and metadata
    """
    global _last_arxiv_call

    # Rate limiting: 3 seconds between calls
    elapsed = time.time() - _last_arxiv_call
    if elapsed < 3.0:
        time.sleep(3.0 - elapsed)

    # Build search query
    search_parts = []
    if query:
        search_parts.append(f"all:{query}")
    if categories:
        cat_parts = [f"cat:{c.strip()}" for c in categories.split(",")]
        search_parts.append(f"({' OR '.join(cat_parts)})")
    if date_from or date_to:
        # Format: submittedDate:[YYYYMMDDHHSS TO YYYYMMDDHHSS]
        df = date_from.replace("-", "") + "0000" if date_from else "000000000000"
        dt = date_to.replace("-", "") + "2359" if date_to else "999912312359"
        search_parts.append(f"submittedDate:[{df}+TO+{dt}]")

    search_query = "+AND+".join(search_parts) if search_parts else "all:*"
    max_results = min(max_results, 100)

    sort_map = {"relevance": "relevance", "date": "submittedDate", "updated": "lastUpdatedDate"}
    sort_val = sort_map.get(sort_by, "relevance")

    url = f"{ARXIV_API}?search_query={urllib.parse.quote(search_query)}&start=0&max_results={max_results}&sortBy={sort_val}&sortOrder={sort_order}"

    try:
        _last_arxiv_call = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "lit-review/1.0"})
        with urllib.request.urlopen(req, timeout=30, context=_ssl_ctx) as resp:
            xml_data = resp.read().decode("utf-8")
    except Exception as e:
        return {"error": f"arXiv API error: {str(e)}", "papers": []}

    # Parse XML
    papers = []
    try:
        root = ET.fromstring(xml_data)
        total = root.find("opensearch:totalResults", {"opensearch": "http://a9.com/-/spec/opensearch/1.1/"})
        total_count = int(total.text) if total is not None else 0

        for entry in root.findall("atom:entry", ARXIV_NS):
            paper_id = entry.find("atom:id", ARXIV_NS).text.strip()
            arxiv_id = paper_id.split("/abs/")[-1].split("v")[0] if "/abs/" in paper_id else paper_id

            title = entry.find("atom:title", ARXIV_NS).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", ARXIV_NS).text.strip().replace("\n", " ")
            published = entry.find("atom:published", ARXIV_NS).text[:10]
            year = int(published[:4]) if published else 0

            authors = []
            for author in entry.findall("atom:author", ARXIV_NS):
                name = author.find("atom:name", ARXIV_NS).text.strip()
                authors.append(name)

            categories_list = []
            for cat in entry.findall("atom:category", ARXIV_NS):
                categories_list.append(cat.get("term", ""))

            primary_cat_el = entry.find("arxiv:primary_category", ARXIV_NS)
            primary_category = primary_cat_el.get("term", "") if primary_cat_el is not None else ""

            doi_el = entry.find("arxiv:doi", ARXIV_NS)
            doi = doi_el.text.strip() if doi_el is not None else ""

            comment_el = entry.find("arxiv:comment", ARXIV_NS)
            comment = comment_el.text.strip() if comment_el is not None else ""

            pdf_url = ""
            for link in entry.findall("atom:link", ARXIV_NS):
                if link.get("title") == "pdf":
                    pdf_url = link.get("href", "")

            papers.append({
                "paper_id": f"arxiv:{arxiv_id}",
                "arxiv_id": arxiv_id,
                "title": title,
                "authors": authors,
                "year": year,
                "abstract": summary,
                "url": paper_id,
                "pdf_url": pdf_url,
                "source": "arxiv",
                "categories": categories_list,
                "primary_category": primary_category,
                "doi": doi,
                "comment": comment,
                "citations": 0,  # arXiv doesn't provide citation count
                "published": published,
            })
    except Exception as e:
        return {"error": f"arXiv parse error: {str(e)}", "papers": []}

    return {
        "source": "arxiv",
        "total": total_count,
        "returned": len(papers),
        "query": query,
        "papers": papers,
    }


# ---------------------------------------------------------------------------
# Semantic Scholar API
# ---------------------------------------------------------------------------

S2_API = "https://api.semanticscholar.org/graph/v1"
S2_RECOMMEND_API = "https://api.semanticscholar.org/recommendations/v1"
_last_s2_call = 0.0


def _s2_request(url: str, api_key: str = "") -> dict | None:
    """Make a request to Semantic Scholar API with rate limiting."""
    global _last_s2_call

    # Rate limiting: 1 req/sec with key, 3 sec without
    delay = 1.0 if api_key else 3.0
    elapsed = time.time() - _last_s2_call
    if elapsed < delay:
        time.sleep(delay - elapsed)

    headers = {"User-Agent": "lit-review/1.0"}
    if api_key:
        headers["x-api-key"] = api_key

    try:
        _last_s2_call = time.time()
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30, context=_ssl_ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            retry_after = int(e.headers.get("Retry-After", "10"))
            time.sleep(retry_after)
            try:
                _last_s2_call = time.time()
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=30, context=_ssl_ctx) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except Exception:
                return {"error": "Semantic Scholar rate limited. Get a free API key at https://www.semanticscholar.org/product/api"}
        return {"error": f"Semantic Scholar HTTP {e.code}"}
    except Exception as e:
        return {"error": f"Semantic Scholar error: {str(e)}"}


def search_semantic_scholar(query: str, max_results: int = 10, year: str = "",
                            fields_of_study: str = "", min_citations: int = 0,
                            api_key: str = "") -> dict:
    """Search Semantic Scholar API.

    Args:
        query: Search query
        max_results: Max results (default 10, max 100)
        year: Year filter (e.g. "2023", "2020-2024", "2020-")
        fields_of_study: e.g. "Computer Science", "Medicine"
        min_citations: Minimum citation count
        api_key: Optional Semantic Scholar API key (auto-read from config if empty)

    Returns:
        dict with papers list and metadata
    """
    if not api_key:
        api_key = get_api_key()
    max_results = min(max_results, 100)

    fields = "paperId,title,abstract,year,citationCount,authors,url,externalIds,openAccessPdf,fieldsOfStudy,venue,publicationTypes"

    params = {
        "query": query,
        "limit": str(max_results),
        "fields": fields,
    }
    if year:
        params["year"] = year
    if fields_of_study:
        params["fieldsOfStudy"] = fields_of_study
    if min_citations > 0:
        params["minCitationCount"] = str(min_citations)

    url = f"{S2_API}/paper/search?{urllib.parse.urlencode(params)}"
    data = _s2_request(url, api_key)

    if data is None:
        return {"error": "Semantic Scholar API request failed", "papers": []}

    papers = []
    for p in data.get("data", []):
        authors = [a.get("name", "") for a in p.get("authors", [])]
        ext_ids = p.get("externalIds", {}) or {}
        arxiv_id = ext_ids.get("ArXiv", "")
        doi = ext_ids.get("DOI", "")

        pdf_info = p.get("openAccessPdf") or {}
        pdf_url = pdf_info.get("url", "")

        papers.append({
            "paper_id": f"s2:{p.get('paperId', '')}",
            "s2_id": p.get("paperId", ""),
            "arxiv_id": arxiv_id,
            "title": p.get("title", ""),
            "authors": authors,
            "year": p.get("year", 0),
            "abstract": p.get("abstract", "") or "",
            "url": p.get("url", ""),
            "pdf_url": pdf_url,
            "source": "semantic-scholar",
            "citations": p.get("citationCount", 0),
            "venue": p.get("venue", ""),
            "fields_of_study": p.get("fieldsOfStudy", []) or [],
            "doi": doi,
        })

    return {
        "source": "semantic-scholar",
        "total": data.get("total", 0),
        "returned": len(papers),
        "query": query,
        "papers": papers,
    }


def get_paper_citations(paper_id: str, max_results: int = 20, api_key: str = "") -> dict:
    """Get papers that cite this paper."""
    if not api_key:
        api_key = get_api_key()
    fields = "title,year,citationCount,authors"
    url = f"{S2_API}/paper/{paper_id}/citations?fields={fields}&limit={max_results}"
    data = _s2_request(url, api_key)

    if data is None:
        return {"error": "Failed to fetch citations", "papers": []}

    papers = []
    for item in data.get("data", []):
        p = item.get("citingPaper", {})
        authors = [a.get("name", "") for a in p.get("authors", [])]
        papers.append({
            "paper_id": f"s2:{p.get('paperId', '')}",
            "title": p.get("title", ""),
            "year": p.get("year", 0),
            "citations": p.get("citationCount", 0),
            "authors": authors,
        })

    return {"count": len(papers), "papers": papers}


def get_paper_references(paper_id: str, max_results: int = 20, api_key: str = "") -> dict:
    """Get papers that this paper references."""
    if not api_key:
        api_key = get_api_key()
    fields = "title,year,citationCount,authors"
    url = f"{S2_API}/paper/{paper_id}/references?fields={fields}&limit={max_results}"
    data = _s2_request(url, api_key)

    if data is None:
        return {"error": "Failed to fetch references", "papers": []}

    papers = []
    for item in data.get("data", []):
        p = item.get("citedPaper", {})
        if not p or not p.get("paperId"):
            continue
        authors = [a.get("name", "") for a in p.get("authors", [])]
        papers.append({
            "paper_id": f"s2:{p.get('paperId', '')}",
            "title": p.get("title", ""),
            "year": p.get("year", 0),
            "citations": p.get("citationCount", 0),
            "authors": authors,
        })

    return {"count": len(papers), "papers": papers}


def get_recommendations(paper_ids: list, max_results: int = 10, api_key: str = "") -> dict:
    """Get paper recommendations based on seed papers."""
    if not api_key:
        api_key = get_api_key()
    fields = "title,abstract,year,citationCount,authors,url"
    positive = ",".join(paper_ids)
    url = f"{S2_RECOMMEND_API}/papers?positivePaperIds={positive}&limit={max_results}&fields={fields}"
    data = _s2_request(url, api_key)

    if data is None:
        return {"error": "Failed to fetch recommendations", "papers": []}

    papers = []
    for p in data.get("recommendedPapers", []):
        authors = [a.get("name", "") for a in p.get("authors", [])]
        papers.append({
            "paper_id": f"s2:{p.get('paperId', '')}",
            "title": p.get("title", ""),
            "year": p.get("year", 0),
            "abstract": p.get("abstract", "") or "",
            "citations": p.get("citationCount", 0),
            "authors": authors,
            "url": p.get("url", ""),
        })

    return {"count": len(papers), "papers": papers}


def search_multi(query: str, sources: list = None, max_results: int = 10,
                 year: str = "", categories: str = "", min_citations: int = 0,
                 api_key: str = "") -> dict:
    if not api_key:
        api_key = get_api_key()
    """Search multiple sources and merge results.

    Args:
        query: Search query
        sources: List of sources ("arxiv", "semantic-scholar"). Default: both.
        max_results: Max results per source
        year: Year filter (for Semantic Scholar)
        categories: arXiv categories
        min_citations: Minimum citation count (for Semantic Scholar)
        api_key: Semantic Scholar API key

    Returns:
        dict with merged papers list
    """
    if sources is None:
        sources = ["arxiv", "semantic-scholar"]

    all_papers = []
    errors = []

    if "arxiv" in sources:
        result = search_arxiv(query, max_results=max_results, categories=categories)
        if "error" in result:
            errors.append(f"arXiv: {result['error']}")
        else:
            all_papers.extend(result["papers"])

    if "semantic-scholar" in sources:
        result = search_semantic_scholar(
            query, max_results=max_results, year=year,
            min_citations=min_citations, api_key=api_key
        )
        if "error" in result:
            errors.append(f"Semantic Scholar: {result['error']}")
        else:
            all_papers.extend(result["papers"])

    # Deduplicate by title similarity
    seen_titles = set()
    unique_papers = []
    for p in all_papers:
        title_key = p["title"].lower().strip()[:80]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_papers.append(p)

    # Sort by citations (descending)
    unique_papers.sort(key=lambda p: p.get("citations", 0), reverse=True)

    return {
        "sources": sources,
        "total_before_dedup": len(all_papers),
        "total_after_dedup": len(unique_papers),
        "query": query,
        "errors": errors,
        "papers": unique_papers,
    }
