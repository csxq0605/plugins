#!/usr/bin/env python3
"""lit-search — CLI for arXiv and Semantic Scholar API.

Usage:
    python lit-search.py search "query" [--sources arxiv,semantic-scholar] [--max 10] [--year 2023-2025]
    python lit-search.py citations ARXIV:2301.00234 [--max 20]
    python lit-search.py references ARXIV:2301.00234 [--max 20]
    python lit-search.py recommend ARXIV:2301.00234,ARXIV:1810.04805 [--max 10]
    python lit-search.py set-key YOUR_API_KEY
    python lit-search.py config

Requires: Python 3.10+, no external dependencies.
API key: set via SEMANTIC_SCHOLAR_API_KEY env var, or 'set-key' command.
"""

import json
import os
import ssl
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

# SSL context for environments without proper cert store
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

# Config
_CONFIG_DIR = Path.home() / ".lit-review"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def _load_config():
    if _CONFIG_FILE.exists():
        try:
            return json.loads(_CONFIG_FILE.read_text("utf-8"))
        except Exception:
            pass
    return {}


def _save_config(config):
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(json.dumps(config, indent=2), "utf-8")


def _get_api_key():
    env = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    if env:
        return env
    return _load_config().get("semantic_scholar_api_key", "")


# ── arXiv ───────────────────────────────────────────────────────────────────

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
_last_arxiv = 0.0


def search_arxiv(query, max_results=10, categories="", year_from="", year_to=""):
    global _last_arxiv
    elapsed = time.time() - _last_arxiv
    if elapsed < 3.0:
        time.sleep(3.0 - elapsed)

    parts = [f"all:{query}"]
    if categories:
        cats = " OR ".join(f"cat:{c.strip()}" for c in categories.split(","))
        parts.append(f"({cats})")
    if year_from or year_to:
        df = year_from.replace("-", "") + "0000" if year_from else "000000000000"
        dt = year_to.replace("-", "") + "2359" if year_to else "999912312359"
        parts.append(f"submittedDate:[{df}+TO+{dt}]")

    q = "+AND+".join(parts)
    url = f"{ARXIV_API}?search_query={urllib.parse.quote(q)}&max_results={min(max_results, 100)}&sortBy=relevance&sortOrder=descending"

    try:
        _last_arxiv = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "lit-review/1.0"})
        with urllib.request.urlopen(req, timeout=30, context=_ssl_ctx) as resp:
            xml_data = resp.read().decode("utf-8")
    except Exception as e:
        return {"error": f"arXiv: {e}", "papers": []}

    papers = []
    root = ET.fromstring(xml_data)
    total_el = root.find("opensearch:totalResults", {"opensearch": "http://a9.com/-/spec/opensearch/1.1/"})
    total = int(total_el.text) if total_el is not None else 0

    for entry in root.findall("atom:entry", ARXIV_NS):
        pid = entry.find("atom:id", ARXIV_NS).text.strip()
        arxiv_id = pid.split("/abs/")[-1].split("v")[0] if "/abs/" in pid else pid
        title = entry.find("atom:title", ARXIV_NS).text.strip().replace("\n", " ")
        summary = entry.find("atom:summary", ARXIV_NS).text.strip().replace("\n", " ")
        published = entry.find("atom:published", ARXIV_NS).text[:10]
        year = int(published[:4]) if published else 0
        authors = [a.find("atom:name", ARXIV_NS).text.strip() for a in entry.findall("atom:author", ARXIV_NS)]
        cats = [c.get("term", "") for c in entry.findall("atom:category", ARXIV_NS)]
        doi_el = entry.find("arxiv:doi", ARXIV_NS)
        doi = doi_el.text.strip() if doi_el is not None else ""
        pdf = ""
        for link in entry.findall("atom:link", ARXIV_NS):
            if link.get("title") == "pdf":
                pdf = link.get("href", "")

        papers.append({
            "paper_id": f"ARXIV:{arxiv_id}",
            "title": title, "authors": authors, "year": year,
            "abstract": summary[:500], "url": pid, "pdf_url": pdf,
            "source": "arxiv", "citations": 0, "doi": doi,
        })

    return {"source": "arxiv", "total": total, "returned": len(papers), "papers": papers}


# ── Semantic Scholar ────────────────────────────────────────────────────────

S2_API = "https://api.semanticscholar.org/graph/v1"
S2_REC = "https://api.semanticscholar.org/recommendations/v1"
_last_s2 = 0.0


def _s2_req(url):
    global _last_s2
    key = _get_api_key()
    delay = 1.0 if key else 3.0
    elapsed = time.time() - _last_s2
    if elapsed < delay:
        time.sleep(delay - elapsed)

    headers = {"User-Agent": "lit-review/1.0"}
    if key:
        headers["x-api-key"] = key

    try:
        _last_s2 = time.time()
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30, context=_ssl_ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            ra = int(e.headers.get("Retry-After", "10"))
            time.sleep(ra)
            try:
                _last_s2 = time.time()
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=30, context=_ssl_ctx) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except Exception:
                pass
        return {"error": f"S2 HTTP {e.code}"}
    except Exception as e:
        return {"error": f"S2: {e}"}


def search_s2(query, max_results=10, year="", min_citations=0):
    fields = "paperId,title,abstract,year,citationCount,authors,url,externalIds,openAccessPdf,venue"
    params = {"query": query, "limit": str(min(max_results, 100)), "fields": fields}
    if year:
        params["year"] = year
    if min_citations:
        params["minCitationCount"] = str(min_citations)

    data = _s2_req(f"{S2_API}/paper/search?{urllib.parse.urlencode(params)}")
    if "error" in data:
        return data

    papers = []
    for p in data.get("data", []):
        authors = [a.get("name", "") for a in p.get("authors", [])]
        ext = p.get("externalIds") or {}
        pdf = (p.get("openAccessPdf") or {}).get("url", "")
        papers.append({
            "paper_id": p.get("paperId", ""),
            "arxiv_id": ext.get("ArXiv", ""),
            "title": p.get("title", ""), "authors": authors,
            "year": p.get("year", 0), "abstract": (p.get("abstract") or "")[:500],
            "url": p.get("url", ""), "pdf_url": pdf,
            "source": "semantic-scholar", "citations": p.get("citationCount", 0),
            "venue": p.get("venue", ""), "doi": ext.get("DOI", ""),
        })

    return {"source": "semantic-scholar", "total": data.get("total", 0), "returned": len(papers), "papers": papers}


def get_citations(paper_id, max_results=20):
    fields = "title,year,citationCount,authors"
    data = _s2_req(f"{S2_API}/paper/{paper_id}/citations?fields={fields}&limit={max_results}")
    if "error" in data:
        return data
    papers = []
    for item in data.get("data", []):
        p = item.get("citingPaper", {})
        papers.append({
            "paper_id": p.get("paperId", ""), "title": p.get("title", ""),
            "year": p.get("year", 0), "citations": p.get("citationCount", 0),
            "authors": [a.get("name", "") for a in p.get("authors", [])],
        })
    return {"count": len(papers), "papers": papers}


def get_references(paper_id, max_results=20):
    fields = "title,year,citationCount,authors"
    data = _s2_req(f"{S2_API}/paper/{paper_id}/references?fields={fields}&limit={max_results}")
    if "error" in data:
        return data
    papers = []
    for item in data.get("data", []):
        p = item.get("citedPaper", {})
        if not p or not p.get("paperId"):
            continue
        papers.append({
            "paper_id": p.get("paperId", ""), "title": p.get("title", ""),
            "year": p.get("year", 0), "citations": p.get("citationCount", 0),
            "authors": [a.get("name", "") for a in p.get("authors", [])],
        })
    return {"count": len(papers), "papers": papers}


def get_recommendations(paper_ids, max_results=10):
    fields = "title,abstract,year,citationCount,authors,url"
    ids = ",".join(paper_ids)
    data = _s2_req(f"{S2_REC}/papers?positivePaperIds={ids}&limit={max_results}&fields={fields}")
    if data and "error" not in data:
        papers = []
        for p in data.get("recommendedPapers", []):
            papers.append({
                "paper_id": p.get("paperId", ""), "title": p.get("title", ""),
                "year": p.get("year", 0), "abstract": (p.get("abstract") or "")[:500],
                "citations": p.get("citationCount", 0),
                "authors": [a.get("name", "") for a in p.get("authors", [])],
                "url": p.get("url", ""),
            })
        return {"count": len(papers), "papers": papers}
    # Fallback: return references of seed papers
    seen = set()
    papers = []
    for pid in paper_ids:
        refs = get_references(pid, max_results=max_results)
        for p in refs.get("papers", []):
            if p["paper_id"] not in seen:
                seen.add(p["paper_id"])
                papers.append(p)
    papers.sort(key=lambda p: p.get("citations", 0), reverse=True)
    return {"count": len(papers[:max_results]), "papers": papers[:max_results],
            "note": "Recommendations API unavailable; returning references instead."}


def search_multi(query, sources, max_results=10, year="", categories="", min_citations=0):
    all_papers = []
    errors = []
    if "arxiv" in sources:
        r = search_arxiv(query, max_results, categories)
        if "error" in r:
            errors.append(f"arXiv: {r['error']}")
        else:
            all_papers.extend(r["papers"])
    if "semantic-scholar" in sources:
        r = search_s2(query, max_results, year, min_citations)
        if "error" in r:
            errors.append(f"S2: {r['error']}")
        else:
            all_papers.extend(r["papers"])

    seen = set()
    unique = []
    for p in all_papers:
        key = p["title"].lower().strip()[:80]
        if key not in seen:
            seen.add(key)
            unique.append(p)
    unique.sort(key=lambda p: p.get("citations", 0), reverse=True)
    return {"sources": sources, "total": len(unique), "query": query, "errors": errors, "papers": unique}


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "set-key":
        if len(sys.argv) < 3:
            print("Usage: lit-search.py set-key YOUR_KEY")
            sys.exit(1)
        key = sys.argv[2]
        config = _load_config()
        config["semantic_scholar_api_key"] = key
        _save_config(config)
        print(json.dumps({"status": "ok", "key": "***" + key[-4:], "file": str(_CONFIG_FILE)}))

    elif cmd == "config":
        key = _get_api_key()
        print(json.dumps({
            "config_file": str(_CONFIG_FILE),
            "api_key": "***" + key[-4:] if key else "(not set)",
            "env_key_set": bool(os.environ.get("SEMANTIC_SCHOLAR_API_KEY")),
        }, indent=2))

    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: lit-search.py search \"query\" [--sources arxiv,semantic-scholar] [--max 10] [--year 2023-2025]")
            sys.exit(1)
        query = sys.argv[2]
        sources = ["arxiv", "semantic-scholar"]
        max_results = 10
        year = ""
        categories = ""
        min_citations = 0
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--sources" and i + 1 < len(sys.argv):
                sources = sys.argv[i + 1].split(",")
                i += 2
            elif sys.argv[i] == "--max" and i + 1 < len(sys.argv):
                max_results = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--year" and i + 1 < len(sys.argv):
                year = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--categories" and i + 1 < len(sys.argv):
                categories = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--min-citations" and i + 1 < len(sys.argv):
                min_citations = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        result = search_multi(query, sources, max_results, year, categories, min_citations)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "citations":
        if len(sys.argv) < 3:
            print("Usage: lit-search.py citations PAPER_ID [--max 20]")
            sys.exit(1)
        paper_id = sys.argv[2]
        max_r = 20
        if "--max" in sys.argv:
            idx = sys.argv.index("--max")
            if idx + 1 < len(sys.argv):
                max_r = int(sys.argv[idx + 1])
        print(json.dumps(get_citations(paper_id, max_r), ensure_ascii=False, indent=2))

    elif cmd == "references":
        if len(sys.argv) < 3:
            print("Usage: lit-search.py references PAPER_ID [--max 20]")
            sys.exit(1)
        paper_id = sys.argv[2]
        max_r = 20
        if "--max" in sys.argv:
            idx = sys.argv.index("--max")
            if idx + 1 < len(sys.argv):
                max_r = int(sys.argv[idx + 1])
        print(json.dumps(get_references(paper_id, max_r), ensure_ascii=False, indent=2))

    elif cmd == "recommend":
        if len(sys.argv) < 3:
            print("Usage: lit-search.py recommend ID1,ID2 [--max 10]")
            sys.exit(1)
        ids = sys.argv[2].split(",")
        max_r = 10
        if "--max" in sys.argv:
            idx = sys.argv.index("--max")
            if idx + 1 < len(sys.argv):
                max_r = int(sys.argv[idx + 1])
        print(json.dumps(get_recommendations(ids, max_r), ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
