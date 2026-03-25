"""
CIT Spark Ingestor v2 — pulls raw data from all 7 actual Cimeika repos.
Updated topology: ci_gitapi + cimeika-backend + ci-memory replaces cit_versel.
"""
import os, json, asyncio, httpx
from pathlib import Path
from typing import List, Dict, Any

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
DATA_SINK = Path("dani/spark/raw")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# АКТУАЛЬНИЙ РЕЄСТР: 7 репозиторіїв
REPOS_CONFIG = {
    # CORE — manifest.json, registry, dani/, abilities/
    "Ihorog/cit": {
        "role": "core_toolkit",
        "files": ["manifest.json", "registry/modules.json", "core/dzerkalo.py"],
        "ext_tree": None,
    },
    # GATEWAY — ecosystem DNA, mesh registry (private → token required)
    "Ihorog/ci_gitapi": {
        "role": "auth_gateway",
        "files": ["ci_mesh_registry.yaml", "app/routes/ecosystem.py", "app/main.py"],
        "ext_tree": None,
    },
    # PLATFORM — 7 modules, CRDT, Yjs
    "Ihorog/cimeika-unified": {
        "role": "unified_platform",
        "files": ["SYSTEM_WILL.md", "backend/app/core/interfaces.py"],
        "ext_tree": ".md",
    },
    # EDGE — TypeScript agents, Cloudflare Workers
    "Ihorog/cimeika-backend": {
        "role": "edge_runtime",
        "files": ["src/index.ts", "src/agents/base-agent.ts", "src/types/env.ts"],
        "ext_tree": ".ts",
    },
    # MEMORY — MIND.md shared AI context
    "Ihorog/ci-memory": {
        "role": "shared_memory",
        "files": ["MIND.md", "CONSTITUTION.md", "REPOS.md"],
        "ext_tree": None,
    },
    # KNOWLEDGE — docs, legends
    "Ihorog/ciwiki": {
        "role": "knowledge_base",
        "files": [],
        "ext_tree": ".md",
    },
    # ASSETS — media index
    "Ihorog/media": {
        "role": "media_assets",
        "files": [],
        "ext_tree": ".json",
    },
}

async def fetch_file(client: httpx.AsyncClient, repo: str, path: str) -> Dict[str, Any]:
    import base64
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    r = await client.get(url, headers=HEADERS)
    if r.status_code == 404:
        return {"repo": repo, "path": path, "content": "", "sha": "", "error": "404"}
    r.raise_for_status()
    data = r.json()
    content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    return {
        "repo": repo,
        "path": path,
        "role": REPOS_CONFIG[repo]["role"],
        "content": content,
        "sha": data["sha"]
    }

async def fetch_tree(client: httpx.AsyncClient, repo: str, ext: str) -> List[str]:
    url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
    r = await client.get(url, headers=HEADERS)
    r.raise_for_status()
    return [i["path"] for i in r.json().get("tree", []) if i["path"].endswith(ext)][:15]  # conservative limit for Termux memory

async def ingest_all() -> List[Dict[str, Any]]:
    DATA_SINK.mkdir(parents=True, exist_ok=True)
    tasks = []
    async with httpx.AsyncClient(timeout=30) as client:
        for repo, cfg in REPOS_CONFIG.items():
            for f in cfg["files"]:
                tasks.append(fetch_file(client, repo, f))
            if cfg["ext_tree"]:
                try:
                    paths = await fetch_tree(client, repo, cfg["ext_tree"])
                    for p in paths:
                        tasks.append(fetch_file(client, repo, p))
                except Exception:
                    pass
        results = await asyncio.gather(*tasks, return_exceptions=True)

    valid = [r for r in results if isinstance(r, dict) and not r.get("error")]
    (DATA_SINK / "raw_corpus.json").write_text(
        json.dumps(valid, ensure_ascii=False, indent=2)
    )
    role_index = {}
    for item in valid:
        role = item.get("role", "unknown")
        role_index.setdefault(role, []).append(item["path"])
    (DATA_SINK / "role_index.json").write_text(
        json.dumps(role_index, ensure_ascii=False, indent=2)
    )
    return valid
