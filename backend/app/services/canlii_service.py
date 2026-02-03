"""
CanLII API Service
Provides access to Canadian case law and legislation database.

CanLII (Canadian Legal Information Institute) is the primary source
for free access to Canadian legal materials.

API Documentation: https://api.canlii.org/v1/
Coverage: Canadian federal and provincial courts, tribunals, legislation
"""

import aiohttp
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class CanLIIService:
    """Service for interacting with CanLII API for Canadian legal research."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CanLII service.

        Args:
            api_key: CanLII API key (required for API access)
                    Get free key at: https://www.canlii.org/en/info/api.html
        """
        self.base_url = "https://api.canlii.org/v1"
        self.api_key = api_key or os.getenv("CANLII_API_KEY")
        
        if not self.api_key:
            logger.warning("CanLII API key not configured - using demo mode")
            
        logger.info(f"CanLIIService initialized (configured: {bool(self.api_key)})")

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to CanLII API."""
        if not self.api_key:
            return self._get_demo_response(endpoint, params)
            
        url = f"{self.base_url}/{endpoint}"
        
        # Add API key to params
        if params is None:
            params = {}
        params["api_key"] = self.api_key

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"CanLII API success: {endpoint}")
                        return data
                    elif response.status == 401:
                        error_msg = "Invalid API key"
                        logger.error(f"CanLII authentication failed: {error_msg}")
                        return {"error": error_msg, "status_code": 401}
                    elif response.status == 429:
                        error_msg = "Rate limit exceeded"
                        logger.warning(f"CanLII rate limit: {error_msg}")
                        return {"error": error_msg, "status_code": 429}
                    else:
                        error_text = await response.text()
                        logger.error(f"CanLII API error {response.status}: {error_text}")
                        return {"error": f"API error: {response.status}", "status_code": response.status}

        except aiohttp.ClientError as e:
            logger.error(f"CanLII connection error: {str(e)}")
            return {"error": f"Connection error: {str(e)}"}
        except Exception as e:
            logger.error(f"CanLII unexpected error: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    def _get_demo_response(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Return demo data when API key is not configured."""
        query = params.get("text", "search") if params else "search"
        
        return {
            "success": True,
            "demo_mode": True,
            "message": "CanLII API key not configured - showing sample Canadian cases",
            "cases": [
                {
                    "caseId": {"en": "2023scc15"},
                    "title": "R. v. Sullivan",
                    "citation": "2023 SCC 15",
                    "databaseId": "csc-scc",
                    "court": "Supreme Court of Canada",
                    "date": "2023-03-17",
                    "url": "https://www.canlii.org/en/ca/scc/doc/2023/2023scc15/2023scc15.html",
                    "summary": f"Supreme Court of Canada decision relevant to: {query}",
                    "jurisdiction": "Federal"
                },
                {
                    "caseId": {"en": "2022onca654"},
                    "title": "Doe v. Metropolitan Toronto (Municipality)",
                    "citation": "2022 ONCA 654",
                    "databaseId": "onca",
                    "court": "Court of Appeal for Ontario",
                    "date": "2022-09-21",
                    "url": "https://www.canlii.org/en/on/onca/doc/2022/2022onca654/2022onca654.html",
                    "summary": f"Ontario Court of Appeal decision related to: {query}",
                    "jurisdiction": "Ontario"
                },
                {
                    "caseId": {"en": "2023bcsc1234"},
                    "title": "Smith v. British Columbia",
                    "citation": "2023 BCSC 1234",
                    "databaseId": "bcsc",
                    "court": "Supreme Court of British Columbia",
                    "date": "2023-06-15",
                    "url": "https://www.canlii.org/en/bc/bcsc/doc/2023/2023bcsc1234/2023bcsc1234.html",
                    "summary": f"BC Supreme Court decision concerning: {query}",
                    "jurisdiction": "British Columbia"
                },
                {
                    "caseId": {"en": "2022qcca890"},
                    "title": "Montreal (City) v. Quebec (AG)",
                    "citation": "2022 QCCA 890",
                    "databaseId": "qcca",
                    "court": "Court of Appeal of Quebec",
                    "date": "2022-11-08",
                    "url": "https://www.canlii.org/en/qc/qcca/doc/2022/2022qcca890/2022qcca890.html",
                    "summary": f"Quebec Court of Appeal ruling on: {query}",
                    "jurisdiction": "Quebec"
                },
                {
                    "caseId": {"en": "2023abca200"},
                    "title": "Calgary (City) v. Alberta Energy Regulator",
                    "citation": "2023 ABCA 200",
                    "databaseId": "abca",
                    "court": "Court of Appeal of Alberta",
                    "date": "2023-08-10",
                    "url": "https://www.canlii.org/en/ab/abca/doc/2023/2023abca200/2023abca200.html",
                    "summary": f"Alberta Court of Appeal decision on: {query}",
                    "jurisdiction": "Alberta"
                }
            ],
            "total_results": 5,
            "note": "To access real Canadian case law, configure CANLII_API_KEY in your environment"
        }

    async def search_cases(
        self,
        query: str,
        database: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        date_after: Optional[str] = None,
        date_before: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search Canadian case law.

        Args:
            query: Search query (e.g., "charter rights", "negligence")
            database: Database identifier (e.g., "csc-scc" for Supreme Court)
            jurisdiction: Province code (e.g., "on", "bc", "qc", "ab")
            date_after: Filter cases after this date (YYYY-MM-DD)
            date_before: Filter cases before this date (YYYY-MM-DD)
            limit: Maximum number of results

        Returns:
            Dictionary with search results
        """
        params = {
            "text": query,
            "resultCount": min(limit, 50)
        }
        
        if database:
            params["databaseId"] = database
        if date_after:
            params["decisionDateAfter"] = date_after
        if date_before:
            params["decisionDateBefore"] = date_before

        endpoint = "search/caseBrowse"
        
        result = await self._make_request(endpoint, params)
        
        if "error" in result:
            return result
            
        return {
            "success": True,
            "query": query,
            "jurisdiction": jurisdiction or "all_canadian",
            **result
        }

    async def get_case_details(self, database_id: str, case_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific case.

        Args:
            database_id: Database identifier (e.g., "csc-scc")
            case_id: Case identifier

        Returns:
            Detailed case information
        """
        endpoint = f"caseBrowse/{database_id}/{case_id}"
        return await self._make_request(endpoint)

    async def search_legislation(
        self,
        query: str,
        jurisdiction: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search Canadian legislation.

        Args:
            query: Search terms
            jurisdiction: Jurisdiction code (e.g., "ca" for federal, "on" for Ontario)
            limit: Maximum results

        Returns:
            Legislation search results
        """
        params = {
            "text": query,
            "resultCount": min(limit, 50)
        }
        
        if jurisdiction:
            params["legislationId"] = jurisdiction

        endpoint = "search/legislationBrowse"
        return await self._make_request(endpoint, params)

    async def get_databases(self) -> Dict[str, Any]:
        """
        Get list of available CanLII databases.

        Returns:
            List of databases with their identifiers
        """
        if not self.api_key:
            return {
                "success": True,
                "databases": [
                    {"id": "csc-scc", "name": "Supreme Court of Canada", "jurisdiction": "Federal"},
                    {"id": "fca-caf", "name": "Federal Court of Appeal", "jurisdiction": "Federal"},
                    {"id": "fc-cf", "name": "Federal Court", "jurisdiction": "Federal"},
                    {"id": "onca", "name": "Court of Appeal for Ontario", "jurisdiction": "Ontario"},
                    {"id": "onsc", "name": "Superior Court of Justice (Ontario)", "jurisdiction": "Ontario"},
                    {"id": "bcca", "name": "Court of Appeal for British Columbia", "jurisdiction": "BC"},
                    {"id": "bcsc", "name": "Supreme Court of British Columbia", "jurisdiction": "BC"},
                    {"id": "abca", "name": "Court of Appeal of Alberta", "jurisdiction": "Alberta"},
                    {"id": "abqb", "name": "Court of Queen's Bench of Alberta", "jurisdiction": "Alberta"},
                    {"id": "qcca", "name": "Court of Appeal of Quebec", "jurisdiction": "Quebec"},
                    {"id": "qccs", "name": "Superior Court of Quebec", "jurisdiction": "Quebec"},
                ]
            }
        
        endpoint = "caseDatabases"
        return await self._make_request(endpoint)


# Convenience function for quick Canadian legal search
async def search_canadian_cases(
    query: str,
    jurisdiction: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Quick search for Canadian case law.
    
    Args:
        query: Search terms
        jurisdiction: Optional province code
        limit: Max results
        
    Returns:
        Search results from CanLII
    """
    service = CanLIIService()
    return await service.search_cases(query, jurisdiction=jurisdiction, limit=limit)


# Convenience function to detect if query is Canadian
def is_canadian_legal_query(query: str) -> bool:
    """
    Detect if a legal search query is related to Canadian law.
    
    Args:
        query: The search query text
        
    Returns:
        True if the query appears to be Canadian-focused
    """
    canadian_indicators = [
        "canada", "canadian", "ontario", "quebec", "british columbia", "alberta",
        "manitoba", "saskatchewan", "nova scotia", "new brunswick", "newfoundland",
        "pei", "prince edward", "yukon", "northwest territories", "nunavut",
        "scc", "onca", "bcca", "abca", "qcca", "federal court of canada",
        "supreme court of canada", "charter", "criminal code of canada",
        "canlii", "toronto", "vancouver", "montreal", "calgary", "ottawa",
        "rcmp", "cra", "immigration canada"
    ]
    
    query_lower = query.lower()
    return any(indicator in query_lower for indicator in canadian_indicators)
