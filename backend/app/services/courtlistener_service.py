"""
CourtListener API Service
Provides access to comprehensive US case law database.

API Documentation: https://www.courtlistener.com/api/rest/v4/
Free Tier: 5,000 requests/hour
Coverage: Millions of US court opinions
"""

import aiohttp
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class CourtListenerService:
    """Service for interacting with CourtListener API."""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize CourtListener service.

        Args:
            api_token: Optional API token for authenticated requests (5,000 req/hour free)
                      Without token: 100 requests/day
                      With token: 5,000 requests/hour
        """
        self.base_url = "https://www.courtlistener.com/api/rest/v4"
        self.api_token = api_token
        self.headers = {}

        if api_token:
            self.headers["Authorization"] = f"Token {api_token}"

        logger.info(f"CourtListenerService initialized (authenticated: {bool(api_token)})")

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to CourtListener API."""
        url = f"{self.base_url}/{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"CourtListener API success: {endpoint}")
                        return data
                    elif response.status == 401:
                        error_msg = "Invalid API token"
                        logger.error(f"CourtListener authentication failed: {error_msg}")
                        return {"error": error_msg, "status_code": 401}
                    elif response.status == 429:
                        error_msg = "Rate limit exceeded. Please try again later."
                        logger.warning(f"CourtListener rate limit: {error_msg}")
                        return {"error": error_msg, "status_code": 429}
                    else:
                        error_text = await response.text()
                        logger.error(f"CourtListener API error {response.status}: {error_text}")
                        return {"error": f"API error: {response.status}", "status_code": response.status}

        except aiohttp.ClientError as e:
            logger.error(f"CourtListener connection error: {str(e)}")
            return {"error": f"Connection error: {str(e)}"}
        except Exception as e:
            logger.error(f"CourtListener unexpected error: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    async def search_cases(
        self,
        query: str,
        court: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        date_filed_after: Optional[str] = None,
        date_filed_before: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search case law opinions.

        Args:
            query: Search query (e.g., "habeas corpus", "negligence personal injury")
            court: Court identifier (e.g., "scotus", "ca9", "nysd")
            jurisdiction: Jurisdiction (e.g., "F" for federal, "S" for state)
            date_filed_after: Filter cases after this date (YYYY-MM-DD)
            date_filed_before: Filter cases before this date (YYYY-MM-DD)
            limit: Maximum number of results (1-100)

        Returns:
            Dictionary with search results including case names, citations, opinions
        """
        params = {
            "type": "o",  # opinions
            "q": query,
            "order_by": "score desc",
            "page_size": min(limit, 100)
        }

        if court:
            params["court"] = court
        if jurisdiction:
            params["stat_Jurisdiction"] = jurisdiction
        if date_filed_after:
            params["filed_after"] = date_filed_after
        if date_filed_before:
            params["filed_before"] = date_filed_before

        logger.info(f"Searching cases: query='{query}', court={court}, limit={limit}")

        result = await self._make_request("search/", params)

        if "error" in result:
            return result

        # Parse and format results
        cases = []
        for item in result.get("results", []):
            case_data = {
                "case_name": item.get("caseName", "Unknown"),
                "court": item.get("court", ""),
                "date_filed": item.get("dateFiled", ""),
                "citation": item.get("citation", []),
                "snippet": item.get("snippet", ""),
                "opinion_url": f"https://www.courtlistener.com{item.get('absolute_url', '')}",
                "docket_number": item.get("docketNumber", ""),
                "status": item.get("status", ""),
                "case_id": item.get("id", "")
            }
            cases.append(case_data)

        return {
            "success": True,
            "query": query,
            "total_results": result.get("count", 0),
            "results_returned": len(cases),
            "cases": cases
        }

    async def get_case_details(self, opinion_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific case opinion.

        Args:
            opinion_id: CourtListener opinion ID

        Returns:
            Detailed case information including full text if available
        """
        logger.info(f"Fetching case details for opinion ID: {opinion_id}")

        result = await self._make_request(f"opinions/{opinion_id}/")

        if "error" in result:
            return result

        case_details = {
            "success": True,
            "case_name": result.get("case_name", "Unknown"),
            "court": result.get("court", ""),
            "date_filed": result.get("date_filed", ""),
            "author": result.get("author_str", ""),
            "type": result.get("type", ""),
            "download_url": result.get("download_url", ""),
            "local_path": result.get("local_path", ""),
            "plain_text": result.get("plain_text", ""),
            "html": result.get("html", ""),
            "html_with_citations": result.get("html_with_citations", "")
        }

        return case_details

    async def search_dockets(
        self,
        query: str,
        court: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search court dockets (case records).

        Args:
            query: Search query
            court: Court identifier
            limit: Maximum results

        Returns:
            Docket search results
        """
        params = {
            "type": "r",  # recap (dockets)
            "q": query,
            "order_by": "score desc",
            "page_size": min(limit, 100)
        }

        if court:
            params["court"] = court

        logger.info(f"Searching dockets: query='{query}', court={court}")

        result = await self._make_request("search/", params)

        if "error" in result:
            return result

        dockets = []
        for item in result.get("results", []):
            docket_data = {
                "case_name": item.get("caseName", "Unknown"),
                "court": item.get("court", ""),
                "date_filed": item.get("dateFiled", ""),
                "docket_number": item.get("docketNumber", ""),
                "docket_url": f"https://www.courtlistener.com{item.get('absolute_url', '')}",
                "description": item.get("description", ""),
                "nature_of_suit": item.get("suitNature", "")
            }
            dockets.append(docket_data)

        return {
            "success": True,
            "query": query,
            "total_results": result.get("count", 0),
            "results_returned": len(dockets),
            "dockets": dockets
        }

    async def get_courts_list(self) -> Dict[str, Any]:
        """
        Get list of all courts in the database.

        Returns:
            List of courts with identifiers and names
        """
        logger.info("Fetching courts list")

        result = await self._make_request("courts/")

        if "error" in result:
            return result

        courts = []
        for court in result.get("results", []):
            courts.append({
                "id": court.get("id", ""),
                "name": court.get("full_name", ""),
                "short_name": court.get("short_name", ""),
                "jurisdiction": court.get("jurisdiction", ""),
                "position": court.get("position", 0)
            })

        return {
            "success": True,
            "total_courts": len(courts),
            "courts": courts
        }


# Global service instance
# Get API token from environment variables for security
courtlistener_service = CourtListenerService(
    api_token=os.getenv("COURTLISTENER_API_TOKEN")
)


# Example court identifiers for reference
COMMON_COURTS = {
    # Federal Courts
    "scotus": "Supreme Court of the United States",
    "ca1": "First Circuit Court of Appeals",
    "ca2": "Second Circuit Court of Appeals",
    "ca3": "Third Circuit Court of Appeals",
    "ca4": "Fourth Circuit Court of Appeals",
    "ca5": "Fifth Circuit Court of Appeals",
    "ca6": "Sixth Circuit Court of Appeals",
    "ca7": "Seventh Circuit Court of Appeals",
    "ca8": "Eighth Circuit Court of Appeals",
    "ca9": "Ninth Circuit Court of Appeals",
    "ca10": "Tenth Circuit Court of Appeals",
    "ca11": "Eleventh Circuit Court of Appeals",
    "cadc": "D.C. Circuit Court of Appeals",
    "cafc": "Federal Circuit Court of Appeals",

    # District Courts (examples)
    "nysd": "Southern District of New York",
    "nynd": "Northern District of New York",
    "cacd": "Central District of California",
    "cand": "Northern District of California",
    "dcd": "District of Columbia",
    "ilnd": "Northern District of Illinois",
    "txsd": "Southern District of Texas",

    # State Courts (examples)
    "cal": "California Supreme Court",
    "ny": "New York Court of Appeals",
    "tex": "Texas Supreme Court",
    "fla": "Florida Supreme Court",
    "ill": "Illinois Supreme Court"
}
