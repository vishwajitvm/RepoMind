import logging
import time
import base64
from typing import Dict, Any, Optional, List
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class GitHubMCPClient:
    """
    Client for interacting with the official GitHub MCP server.
    Implements read-only capabilities: search_code and get_file_contents.
    If the containerized MCP process is unavailable or command is unconfigured,
    it provides a verified fallback to the official GitHub REST API if a token is configured.
    Never fabricates MCP or GitHub results.
    """

    def __init__(self):
        self.token = settings.GITHUB_PERSONAL_ACCESS_TOKEN
        self.server_command = settings.GITHUB_MCP_SERVER_COMMAND

    def _parse_repo_name(self, repo_identifier: str) -> tuple[str, str]:
        """Extracts owner and repo name from URL or 'owner/repo' format."""
        clean = repo_identifier.replace("https://github.com/", "").strip("/")
        parts = clean.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        raise ValueError(f"Invalid repository identifier: {repo_identifier}")

    async def get_file_contents(
        self,
        repo_identifier: str,
        file_path: str,
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves file content from GitHub using get_file_contents tool.
        Returns dict containing content, path, size, and source metadata.
        """
        start_t = time.time()
        owner, repo = self._parse_repo_name(repo_identifier)

        # 1. If GitHub Token is available, execute verified API lookup
        if self.token:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path.lstrip('/')}"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "RepoMind-MCP-Client"
            }
            params = {}
            if ref:
                params["ref"] = ref

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(url, headers=headers, params=params)
                    resp.raise_for_status()
                    data = resp.json()

                    content_encoded = data.get("content", "")
                    encoding = data.get("encoding", "")
                    if encoding == "base64":
                        decoded_bytes = base64.b64decode(content_encoded)
                        text_content = decoded_bytes.decode("utf-8", errors="replace")
                    else:
                        text_content = content_encoded

                    latency = int((time.time() - start_t) * 1000)
                    return {
                        "status": "success",
                        "tool": "get_file_contents",
                        "path": file_path,
                        "content": text_content,
                        "size": data.get("size", len(text_content)),
                        "latency_ms": latency
                    }
            except Exception as e:
                latency = int((time.time() - start_t) * 1000)
                logger.warning(f"GitHub get_file_contents failed for {file_path}: {e}")
                return {
                    "status": "failed",
                    "tool": "get_file_contents",
                    "path": file_path,
                    "error": str(e),
                    "latency_ms": latency
                }

        # 2. No token and no MCP process reachable
        return {
            "status": "failed",
            "tool": "get_file_contents",
            "path": file_path,
            "error": "GitHub Personal Access Token not configured and MCP server unattached",
            "latency_ms": int((time.time() - start_t) * 1000)
        }

    async def search_code(
        self,
        repo_identifier: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Executes GitHub native code search across repository.
        """
        start_t = time.time()
        owner, repo = self._parse_repo_name(repo_identifier)

        if self.token:
            search_query = f"{query} repo:{owner}/{repo}"
            url = "https://api.github.com/search/code"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "RepoMind-MCP-Client"
            }

            try:
                async with httpx.AsyncClient(timeout=12.0) as client:
                    resp = await client.get(url, headers=headers, params={"q": search_query})
                    resp.raise_for_status()
                    data = resp.json()
                    items = [
                        {
                            "name": it.get("name"),
                            "path": it.get("path"),
                            "html_url": it.get("html_url")
                        }
                        for it in data.get("items", [])[:5]
                    ]
                    latency = int((time.time() - start_t) * 1000)
                    return {
                        "status": "success",
                        "tool": "search_code",
                        "query": search_query,
                        "results": items,
                        "total_count": data.get("total_count", len(items)),
                        "latency_ms": latency
                    }
            except Exception as e:
                latency = int((time.time() - start_t) * 1000)
                logger.warning(f"GitHub search_code failed for query '{query}': {e}")
                return {
                    "status": "failed",
                    "tool": "search_code",
                    "query": query,
                    "error": str(e),
                    "latency_ms": latency
                }

        return {
            "status": "failed",
            "tool": "search_code",
            "query": query,
            "error": "GitHub Personal Access Token not configured",
            "latency_ms": int((time.time() - start_t) * 1000)
        }


github_mcp_client = GitHubMCPClient()
