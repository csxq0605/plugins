"""Literature Review tools — Nexgent ToolRegistry integration.

Provides multi-source academic search, paper analysis,
citation network exploration, and review synthesis.
"""

import json
import os
import hashlib
from typing import Any
from datetime import datetime


# ---------------------------------------------------------------------------
# Paper and workspace management
# ---------------------------------------------------------------------------

class Paper:
    """Represents a single academic paper."""

    def __init__(self, paper_id: str, title: str, authors: list, year: int,
                 abstract: str = "", url: str = "", source: str = "",
                 citations: int = 0, doi: str = ""):
        self.paper_id = paper_id
        self.title = title
        self.authors = authors
        self.year = year
        self.abstract = abstract
        self.url = url
        self.source = source
        self.citations = citations
        self.doi = doi
        self.analyses = {}
        self.downloaded_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "abstract": self.abstract,
            "url": self.url,
            "source": self.source,
            "citations": self.citations,
            "doi": self.doi,
            "analyses": self.analyses,
            "downloaded_at": self.downloaded_at,
        }


class ResearchWorkspace:
    """Manages a research workspace with papers and analyses."""

    def __init__(self, workspace_id: str, topic: str):
        self.workspace_id = workspace_id
        self.topic = topic
        self.papers: dict[str, Paper] = {}
        self.search_history = []
        self.created_at = datetime.now().isoformat()

    def add_paper(self, paper: Paper) -> bool:
        if paper.paper_id in self.papers:
            return False
        self.papers[paper.paper_id] = paper
        return True

    def get_paper(self, paper_id: str) -> Paper | None:
        return self.papers.get(paper_id)

    def list_papers(self) -> list:
        return [p.to_dict() for p in self.papers.values()]

    def search_papers(self, query: str) -> list:
        """Simple keyword search over local papers."""
        query_lower = query.lower()
        results = []
        for p in self.papers.values():
            if (query_lower in p.title.lower() or
                query_lower in p.abstract.lower() or
                any(query_lower in a.lower() for a in p.authors)):
                results.append(p.to_dict())
        return results

    def to_dict(self) -> dict:
        return {
            "workspace_id": self.workspace_id,
            "topic": self.topic,
            "papers_count": len(self.papers),
            "search_history": self.search_history,
            "created_at": self.created_at,
        }


# Global workspace store
_workspaces: dict[str, ResearchWorkspace] = {}
_workspace_counter = 0


def _get_next_workspace_id() -> str:
    global _workspace_counter
    _workspace_counter += 1
    return f"ws-{_workspace_counter:04d}"


def _generate_paper_id(title: str, source: str) -> str:
    """Generate a deterministic paper ID from title and source."""
    raw = f"{title.lower().strip()}:{source}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

def _lit_create_workspace(params: dict) -> str:
    """Create a new research workspace."""
    topic = params.get("topic", "General Research")
    ws_id = _get_next_workspace_id()
    ws = ResearchWorkspace(ws_id, topic)
    _workspaces[ws_id] = ws

    return json.dumps({
        "workspace_id": ws_id,
        "topic": topic,
        "message": f"Research workspace '{ws_id}' created for topic: {topic}",
    })


def _lit_add_paper(params: dict) -> str:
    """Add a paper to the workspace."""
    workspace_id = params.get("workspace_id", "")
    if workspace_id not in _workspaces:
        return json.dumps({"error": f"Workspace not found: {workspace_id}"})

    ws = _workspaces[workspace_id]
    title = params.get("title", "")
    if not title:
        return json.dumps({"error": "title is required"})

    paper_id = _generate_paper_id(title, params.get("source", ""))
    paper = Paper(
        paper_id=paper_id,
        title=title,
        authors=params.get("authors", []),
        year=params.get("year", 0),
        abstract=params.get("abstract", ""),
        url=params.get("url", ""),
        source=params.get("source", ""),
        citations=params.get("citations", 0),
        doi=params.get("doi", ""),
    )

    if ws.add_paper(paper):
        return json.dumps({
            "workspace_id": workspace_id,
            "paper_id": paper_id,
            "total_papers": len(ws.papers),
            "message": f"Paper added: {title}",
        })
    return json.dumps({
        "workspace_id": workspace_id,
        "paper_id": paper_id,
        "message": f"Paper already exists: {title}",
    })


def _lit_get_paper(params: dict) -> str:
    """Get paper details by ID."""
    workspace_id = params.get("workspace_id", "")
    if workspace_id not in _workspaces:
        return json.dumps({"error": f"Workspace not found: {workspace_id}"})

    ws = _workspaces[workspace_id]
    paper_id = params.get("paper_id", "")
    paper = ws.get_paper(paper_id)

    if paper:
        return json.dumps(paper.to_dict(), ensure_ascii=False)
    return json.dumps({"error": f"Paper not found: {paper_id}"})


def _lit_list_papers(params: dict) -> str:
    """List all papers in the workspace."""
    workspace_id = params.get("workspace_id", "")
    if workspace_id not in _workspaces:
        return json.dumps({"error": f"Workspace not found: {workspace_id}"})

    ws = _workspaces[workspace_id]
    papers = ws.list_papers()

    # Optional sorting
    sort_by = params.get("sort_by", "year")
    if sort_by == "year":
        papers.sort(key=lambda p: p.get("year", 0), reverse=True)
    elif sort_by == "citations":
        papers.sort(key=lambda p: p.get("citations", 0), reverse=True)

    return json.dumps({
        "workspace_id": workspace_id,
        "count": len(papers),
        "papers": papers,
    }, ensure_ascii=False)


def _lit_search_local(params: dict) -> str:
    """Search papers in the local workspace."""
    workspace_id = params.get("workspace_id", "")
    if workspace_id not in _workspaces:
        return json.dumps({"error": f"Workspace not found: {workspace_id}"})

    ws = _workspaces[workspace_id]
    query = params.get("query", "")
    if not query:
        return json.dumps({"error": "query is required"})

    results = ws.search_papers(query)
    return json.dumps({
        "workspace_id": workspace_id,
        "query": query,
        "count": len(results),
        "results": results,
    }, ensure_ascii=False)


def _lit_add_analysis(params: dict) -> str:
    """Add analysis results to a paper."""
    workspace_id = params.get("workspace_id", "")
    if workspace_id not in _workspaces:
        return json.dumps({"error": f"Workspace not found: {workspace_id}"})

    ws = _workspaces[workspace_id]
    paper_id = params.get("paper_id", "")
    paper = ws.get_paper(paper_id)

    if not paper:
        return json.dumps({"error": f"Paper not found: {paper_id}"})

    analysis_type = params.get("type", "general")
    content = params.get("content", "")

    paper.analyses[analysis_type] = {
        "content": content,
        "added_at": datetime.now().isoformat(),
    }

    return json.dumps({
        "workspace_id": workspace_id,
        "paper_id": paper_id,
        "analysis_type": analysis_type,
        "message": f"Analysis added to paper: {paper.title}",
    })


def _lit_synthesize(params: dict) -> str:
    """Get synthesis data for papers in the workspace."""
    workspace_id = params.get("workspace_id", "")
    if workspace_id not in _workspaces:
        return json.dumps({"error": f"Workspace not found: {workspace_id}"})

    ws = _workspaces[workspace_id]
    papers = list(ws.papers.values())

    if not papers:
        return json.dumps({"error": "No papers in workspace"})

    # Build synthesis data
    by_year = {}
    by_source = {}
    total_citations = 0

    for p in papers:
        by_year[p.year] = by_year.get(p.year, 0) + 1
        by_source[p.source] = by_source.get(p.source, 0) + 1
        total_citations += p.citations

    # Find most cited
    most_cited = sorted(papers, key=lambda p: p.citations, reverse=True)[:5]

    # Find most recent
    most_recent = sorted(papers, key=lambda p: p.year, reverse=True)[:5]

    return json.dumps({
        "workspace_id": workspace_id,
        "topic": ws.topic,
        "total_papers": len(papers),
        "total_citations": total_citations,
        "distribution": {
            "by_year": by_year,
            "by_source": by_source,
        },
        "most_cited": [{"title": p.title, "citations": p.citations, "year": p.year} for p in most_cited],
        "most_recent": [{"title": p.title, "year": p.year, "source": p.source} for p in most_recent],
    }, ensure_ascii=False)


def _lit_list_workspaces(params: dict) -> str:
    """List all research workspaces."""
    workspaces = [ws.to_dict() for ws in _workspaces.values()]
    return json.dumps({
        "count": len(workspaces),
        "workspaces": workspaces,
    }, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Config handlers
# ---------------------------------------------------------------------------

def _lit_set_key(params: dict) -> str:
    """Set Semantic Scholar API key."""
    try:
        from .search_engine import set_api_key, get_config
    except ImportError:
        from search_engine import set_api_key, get_config

    key = params.get("key", "")
    if not key:
        return json.dumps({"error": "key is required"})

    result = set_api_key(key)
    config = get_config()
    return json.dumps({**result, **config}, ensure_ascii=False)


def _lit_get_config(params: dict) -> str:
    """Get current lit-review configuration."""
    try:
        from .search_engine import get_config
    except ImportError:
        from search_engine import get_config

    return json.dumps(get_config(), ensure_ascii=False)


# ---------------------------------------------------------------------------
# API search handlers
# ---------------------------------------------------------------------------

def _lit_search_web(params: dict) -> str:
    """Search papers via arXiv and Semantic Scholar APIs."""
    try:
        from .search_engine import search_multi, search_arxiv, search_semantic_scholar
    except ImportError:
        from search_engine import search_multi, search_arxiv, search_semantic_scholar

    query = params.get("query", "")
    if not query:
        return json.dumps({"error": "query is required"})

    sources_param = params.get("sources", "arxiv,semantic-scholar")
    sources = [s.strip() for s in sources_param.split(",")]
    max_results = params.get("max_results", 10)
    year = params.get("year", "")
    categories = params.get("categories", "")
    min_citations = params.get("min_citations", 0)

    result = search_multi(
        query=query,
        sources=sources,
        max_results=max_results,
        year=year,
        categories=categories,
        min_citations=min_citations,
    )

    return json.dumps(result, ensure_ascii=False)


def _lit_citations(params: dict) -> str:
    """Get papers that cite a given paper."""
    try:
        from .search_engine import get_paper_citations
    except ImportError:
        from search_engine import get_paper_citations

    paper_id = params.get("paper_id", "")
    if not paper_id:
        return json.dumps({"error": "paper_id is required"})

    max_results = params.get("max_results", 20)

    result = get_paper_citations(paper_id, max_results=max_results)
    return json.dumps(result, ensure_ascii=False)


def _lit_references(params: dict) -> str:
    """Get papers referenced by a given paper."""
    try:
        from .search_engine import get_paper_references
    except ImportError:
        from search_engine import get_paper_references

    paper_id = params.get("paper_id", "")
    if not paper_id:
        return json.dumps({"error": "paper_id is required"})

    max_results = params.get("max_results", 20)

    result = get_paper_references(paper_id, max_results=max_results)
    return json.dumps(result, ensure_ascii=False)


def _lit_recommend(params: dict) -> str:
    """Get paper recommendations based on seed papers."""
    try:
        from .search_engine import get_recommendations
    except ImportError:
        from search_engine import get_recommendations

    paper_ids = params.get("paper_ids", [])
    if not paper_ids:
        return json.dumps({"error": "paper_ids is required (list of Semantic Scholar paper IDs)"})

    max_results = params.get("max_results", 10)

    result = get_recommendations(paper_ids, max_results=max_results)
    return json.dumps(result, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

def get_tools() -> list:
    """Return literature review tool definitions for Nexgent's ToolRegistry."""
    try:
        from nexgent.tools.registry import ToolDef
        from nexgent.permissions import Permission
        _has_tooldef = True
    except ImportError:
        _has_tooldef = False

    tools_raw = [
        # ── Config tools ────────────────────────────────────────────
        {
            "name": "lit_set_key",
            "description": (
                "Set Semantic Scholar API key. Saved to ~/.lit-review/config.json. "
                "Get a free key at https://www.semanticscholar.org/product/api"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Semantic Scholar API key"},
                },
                "required": ["key"],
            },
            "handler": _lit_set_key,
            "permission": "write",
        },
        {
            "name": "lit_get_config",
            "description": "Show current lit-review configuration (API key status, config file path).",
            "parameters": {
                "type": "object",
                "properties": {},
            },
            "handler": _lit_get_config,
            "permission": "read",
        },
        # ── Workspace tools ─────────────────────────────────────────
        {
            "name": "lit_create_workspace",
            "description": "Create a new research workspace for a specific topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Research topic"},
                },
                "required": ["topic"],
            },
            "handler": _lit_create_workspace,
            "permission": "write",
        },
        {
            "name": "lit_add_paper",
            "description": "Add a paper to the research workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "title": {"type": "string", "description": "Paper title"},
                    "authors": {"type": "array", "items": {"type": "string"}, "description": "Author list"},
                    "year": {"type": "integer", "description": "Publication year"},
                    "abstract": {"type": "string", "description": "Paper abstract"},
                    "url": {"type": "string", "description": "Paper URL"},
                    "source": {"type": "string", "description": "Source (arxiv, semantic-scholar, google-scholar)"},
                    "citations": {"type": "integer", "description": "Citation count"},
                    "doi": {"type": "string", "description": "DOI"},
                },
                "required": ["workspace_id", "title"],
            },
            "handler": _lit_add_paper,
            "permission": "write",
        },
        {
            "name": "lit_get_paper",
            "description": "Get detailed information about a paper.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "paper_id": {"type": "string"},
                },
                "required": ["workspace_id", "paper_id"],
            },
            "handler": _lit_get_paper,
            "permission": "read",
        },
        {
            "name": "lit_list_papers",
            "description": "List all papers in the workspace, sorted by year or citations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "sort_by": {"type": "string", "enum": ["year", "citations"], "description": "Sort order (default: year)"},
                },
                "required": ["workspace_id"],
            },
            "handler": _lit_list_papers,
            "permission": "read",
        },
        {
            "name": "lit_search_local",
            "description": "Search papers in the local workspace by keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["workspace_id", "query"],
            },
            "handler": _lit_search_local,
            "permission": "read",
        },
        {
            "name": "lit_add_analysis",
            "description": "Add analysis results (methodology, findings, limitations) to a paper.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "paper_id": {"type": "string"},
                    "type": {"type": "string", "description": "Analysis type (methodology, findings, limitations, general)"},
                    "content": {"type": "string", "description": "Analysis content"},
                },
                "required": ["workspace_id", "paper_id", "type", "content"],
            },
            "handler": _lit_add_analysis,
            "permission": "write",
        },
        {
            "name": "lit_synthesize",
            "description": "Get synthesis data for all papers in the workspace (distribution, most cited, trends).",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                },
                "required": ["workspace_id"],
            },
            "handler": _lit_synthesize,
            "permission": "read",
        },
        {
            "name": "lit_list_workspaces",
            "description": "List all research workspaces.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
            "handler": _lit_list_workspaces,
            "permission": "read",
        },
        # ── API search tools ────────────────────────────────────────
        {
            "name": "lit_search_web",
            "description": (
                "Search papers via arXiv and Semantic Scholar APIs. "
                "Returns deduplicated results sorted by citation count. "
                "Supports year/category filters and minimum citation threshold."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "sources": {"type": "string", "description": "Comma-separated sources: arxiv, semantic-scholar (default: both)"},
                    "max_results": {"type": "integer", "description": "Max results per source (default: 10, max: 100)"},
                    "year": {"type": "string", "description": "Year filter for Semantic Scholar (e.g. '2023', '2020-2024')"},
                    "categories": {"type": "string", "description": "arXiv categories (e.g. cs.AI,cs.LG)"},
                    "min_citations": {"type": "integer", "description": "Minimum citation count (Semantic Scholar)"},
                },
                "required": ["query"],
            },
            "handler": _lit_search_web,
            "permission": "write",
        },
        {
            "name": "lit_citations",
            "description": "Get papers that cite a given paper (via Semantic Scholar). Use paper ID like 'ARXIV:2301.00234' or S2 ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "Paper ID (ARXIV:xxx, DOI:xxx, or S2 ID)"},
                    "max_results": {"type": "integer", "description": "Max results (default: 20)"},
                },
                "required": ["paper_id"],
            },
            "handler": _lit_citations,
            "permission": "read",
        },
        {
            "name": "lit_references",
            "description": "Get papers referenced by a given paper (via Semantic Scholar). Use paper ID like 'ARXIV:2301.00234' or S2 ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "Paper ID (ARXIV:xxx, DOI:xxx, or S2 ID)"},
                    "max_results": {"type": "integer", "description": "Max results (default: 20)"},
                },
                "required": ["paper_id"],
            },
            "handler": _lit_references,
            "permission": "read",
        },
        {
            "name": "lit_recommend",
            "description": "Get paper recommendations based on seed papers (via Semantic Scholar). Pass paper IDs you like.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_ids": {"type": "array", "items": {"type": "string"}, "description": "List of seed paper IDs (S2 IDs or ARXIV:xxx)"},
                    "max_results": {"type": "integer", "description": "Max recommendations (default: 10)"},
                },
                "required": ["paper_ids"],
            },
            "handler": _lit_recommend,
            "permission": "read",
        },
    ]

    if _has_tooldef:
        perm_map = {"read": Permission.READ, "write": Permission.WRITE}
        return [
            ToolDef(
                name=t["name"],
                description=t["description"],
                parameters=t["parameters"],
                handler=t["handler"],
                permission=perm_map.get(t["permission"], Permission.WRITE),
                is_read_only=(t["permission"] == "read"),
                is_concurrency_safe=False,
            )
            for t in tools_raw
        ]

    return tools_raw


def get_permissions() -> dict:
    """Return permission descriptions for each tool."""
    return {
        "lit_set_key": "Set Semantic Scholar API key",
        "lit_get_config": "Show current configuration",
        "lit_create_workspace": "Create a research workspace",
        "lit_add_paper": "Add a paper to workspace",
        "lit_get_paper": "Get paper details",
        "lit_list_papers": "List papers in workspace",
        "lit_search_local": "Search papers locally",
        "lit_add_analysis": "Add analysis to paper",
        "lit_synthesize": "Get synthesis data",
        "lit_list_workspaces": "List all workspaces",
        "lit_search_web": "Search papers via APIs",
        "lit_citations": "Get paper citations",
        "lit_references": "Get paper references",
        "lit_recommend": "Get paper recommendations",
    }


def call_tool(name: str, args: dict):
    """Dispatch a tool call by name."""
    tool_map = {
        "lit_set_key": _lit_set_key,
        "lit_get_config": _lit_get_config,
        "lit_create_workspace": _lit_create_workspace,
        "lit_add_paper": _lit_add_paper,
        "lit_get_paper": _lit_get_paper,
        "lit_list_papers": _lit_list_papers,
        "lit_search_local": _lit_search_local,
        "lit_add_analysis": _lit_add_analysis,
        "lit_synthesize": _lit_synthesize,
        "lit_list_workspaces": _lit_list_workspaces,
        "lit_search_web": _lit_search_web,
        "lit_citations": _lit_citations,
        "lit_references": _lit_references,
        "lit_recommend": _lit_recommend,
    }
    func = tool_map.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(args)
    except Exception as e:
        return {"error": str(e)}
