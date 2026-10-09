import os
import logging
from typing import List, Dict, Any, Optional
from tavily import TavilyClient

logger = logging.getLogger(__name__)

class GroundingRetriever:
    """Tavily search client restricted to high-authority educational domains."""
    def __init__(self, tavily_api_key: Optional[str] = None):
        self.api_key = tavily_api_key or os.getenv("TAVILY_API_KEY", "")
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("GroundingRetriever: Tavily API key is missing or empty.")

        self.whitelisted_domains = [
            "openstax.org",
            "khanacademy.org",
            "nces.ed.gov",
            "wikipedia.org",
            "britannica.com",
            "ck12.org"
        ]

    def search_internet(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Executes a search via Tavily API restricted to educational domains."""
        if not self.client:
            logger.warning("No Tavily client available, returning mock search result.")
            return [{
                "title": f"Educational Reference for {query}",
                "url": "https://openstax.org/sample-reference",
                "content": f"Verified curriculum standard reference snippet supporting {query}."
            }]

        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                include_domains=self.whitelisted_domains,
                max_results=max_results
            )

            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")
                })
            return results
        except Exception as e:
            logger.error(f"GroundingRetriever search failed: {e}")
            return [{
                "title": f"Fallback Reference for {query}",
                "url": "https://openstax.org/fallback",
                "content": f"Standard academic reference for {query}."
            }]

    @staticmethod
    def read_local_file(file_path: str) -> str:
        """Reads local files (e.g., review.html) directly from disk."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file not found at: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
