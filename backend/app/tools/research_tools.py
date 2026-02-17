"""Research Tools - Legal Research and Document Management.

Features:
- Legal research for Canada (CanLII) and US (CourtListener)
- Research project management
- Document storage and organization
- Report generation
- File history maintenance
- Business plan and general research support
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import random

from .base_tool import BaseTool, ToolResult, ToolCategory

logger = logging.getLogger(__name__)


class ResearchType(str, Enum):
    """Types of research."""
    LEGAL_CANADA = "legal_canada"
    LEGAL_US = "legal_us"
    BUSINESS = "business"
    MARKET = "market"
    GENERAL = "general"


class DocumentType(str, Enum):
    """Document types."""
    LEGAL_BRIEF = "legal_brief"
    BUSINESS_PLAN = "business_plan"
    RESEARCH_REPORT = "research_report"
    MEMO = "memo"
    CONTRACT = "contract"
    OTHER = "other"


# ============================================
# LEGAL RESEARCH TOOLS
# ============================================

class GetLegalCaseDetailsTool(BaseTool):
    """Get detailed information about a specific legal case."""

    def __init__(self):
        super().__init__(
            name="get_legal_case_details",
            description="Get detailed information about a specific US legal case including full opinion text if available",
            category=ToolCategory.RESEARCH
        )

    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_read permission"
            )

        opinion_id = parameters.get("opinion_id")

        if not opinion_id:
            return ToolResult(
                success=False,
                data=None,
                message="Missing opinion ID",
                error="Opinion ID is required"
            )

        try:
            from app.services.courtlistener_service import courtlistener_service

            logger.info(f"Fetching case details for opinion ID: {opinion_id}")

            # Get case details from CourtListener - REAL API CALL
            case_details = await courtlistener_service.get_case_details(opinion_id)

            if not case_details.get("success"):
                error_msg = case_details.get("error", "Unknown error")
                return ToolResult(
                    success=False,
                    data=None,
                    message=f"Failed to get case details: {error_msg}",
                    error=error_msg
                )

            logger.info(f"Case details retrieved for {user_id}")

            return ToolResult(
                success=True,
                data=case_details,
                message=f"Retrieved case details for opinion ID {opinion_id}"
            )

        except Exception as e:
            logger.error(f"Failed to get case details: {str(e)}")
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to get case details: {str(e)}",
                error=str(e)
            )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "opinion_id": {
                        "type": "integer",
                        "description": "CourtListener opinion ID to retrieve details for"
                    }
                },
                "required": ["opinion_id"]
            }
        }


class SearchLegalDocketsTool(BaseTool):
    """Search court dockets (case records and filings)."""

    def __init__(self):
        super().__init__(
            name="search_legal_dockets",
            description="Search court dockets to find case records, filings, and procedural history",
            category=ToolCategory.RESEARCH
        )

    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_read permission"
            )

        query = parameters.get("query")
        court = parameters.get("court")
        limit = parameters.get("limit", 10)

        if not query:
            return ToolResult(
                success=False,
                data=None,
                message="Missing query",
                error="Search query is required"
            )

        try:
            from app.services.courtlistener_service import courtlistener_service

            logger.info(f"Searching dockets: query='{query}', court={court}")

            # Search dockets using CourtListener - REAL API CALL
            docket_result = await courtlistener_service.search_dockets(
                query=query,
                court=court,
                limit=min(limit, 20)
            )

            if not docket_result.get("success"):
                error_msg = docket_result.get("error", "Unknown error")
                return ToolResult(
                    success=False,
                    data=None,
                    message=f"Failed to search dockets: {error_msg}",
                    error=error_msg
                )

            logger.info(f"Docket search completed for {user_id}: Found {len(docket_result.get('dockets', []))} dockets")

            return ToolResult(
                success=True,
                data=docket_result,
                message=f"Found {docket_result.get('total_results', 0)} total dockets, returning {docket_result.get('results_returned', 0)}"
            )

        except Exception as e:
            logger.error(f"Failed to search dockets: {str(e)}")
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to search dockets: {str(e)}",
                error=str(e)
            )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for docket records"
                    },
                    "court": {
                        "type": "string",
                        "description": "Specific court identifier to search"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (1-20)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }


class SearchLegalCanadaTool(BaseTool):
    """Search Canadian legal resources (CanLII)."""
    
    def __init__(self):
        super().__init__(
            name="search_legal_canada",
            description="Search Canadian legal cases, statutes, and regulations via CanLII",
            category=ToolCategory.RESEARCH
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_read permission"
            )
        
        query = parameters.get("query")
        jurisdiction = parameters.get("jurisdiction", "federal")  # federal, ontario, bc, alberta, etc.
        doc_type = parameters.get("doc_type")  # case, statute, regulation
        date_from = parameters.get("date_from")
        
        if not query:
            return ToolResult(
                success=False,
                data=None,
                message="Missing query",
                error="Search query is required"
            )
        
        try:
            # Use real CanLII service
            from app.services.canlii_service import CanLIIService
            
            canlii_service = CanLIIService()
            
            # Map jurisdiction codes
            jurisdiction_map = {
                "federal": None,
                "ontario": "on",
                "bc": "bc",
                "alberta": "ab",
                "quebec": "qc",
                "manitoba": "mb",
                "saskatchewan": "sk",
                "nova_scotia": "ns",
                "new_brunswick": "nb",
                "newfoundland": "nl",
            }
            
            prov_code = jurisdiction_map.get(jurisdiction.lower())
            
            # Search cases
            case_result = await canlii_service.search_cases(
                query=query,
                jurisdiction=prov_code,
                limit=10
            )
            
            if "error" in case_result and not case_result.get("demo_mode"):
                return ToolResult(
                    success=False,
                    data=None,
                    message=f"CanLII search failed: {case_result.get('error')}",
                    error=case_result.get('error')
                )
            
            # Format results
            results = []
            cases = case_result.get("cases", [])
            
            for case in cases:
                results.append({
                    "type": "case",
                    "title": case.get("title", "Unknown"),
                    "citation": case.get("citation", ""),
                    "court": case.get("court", "Unknown"),
                    "date": case.get("date", ""),
                    "jurisdiction": case.get("jurisdiction", jurisdiction.upper()),
                    "summary": case.get("summary", ""),
                    "url": case.get("url", ""),
                    "database_id": case.get("databaseId", ""),
                    "case_id": case.get("caseId", {}).get("en", "")
                })
            
            # Also search legislation if requested
            if not doc_type or doc_type == "statute":
                legislation_result = await canlii_service.search_legislation(
                    query=query,
                    jurisdiction=prov_code,
                    limit=5
                )
                
                if legislation_result and not legislation_result.get("error"):
                    for statute in legislation_result.get("legislation", []):
                        results.append({
                            "type": "statute",
                            "title": statute.get("title", "Unknown"),
                            "jurisdiction": statute.get("jurisdiction", jurisdiction.upper()),
                            "url": statute.get("url", "")
                        })
            
            logger.info(f"Canadian legal search completed for {user_id}: {query} - Found {len(results)} results")
            
            return ToolResult(
                success=True,
                data={
                    "search_id": f"CA-LEG-{random.randint(100000, 999999)}",
                    "query": query,
                    "jurisdiction": jurisdiction,
                    "results": results,
                    "total_results": len(results),
                    "sources": ["CanLII"],
                    "searched_at": datetime.now().isoformat(),
                    "demo_mode": case_result.get("demo_mode", False),
                    "note": case_result.get("note", "")
                },
                message=f"Found {len(results)} Canadian legal results for '{query}'"
            )
            
        except Exception as e:
            logger.error(f"Canadian legal search error: {str(e)}")
            return ToolResult(
                success=False,
                data=None,
                message=f"Canadian legal search failed: {str(e)}",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Legal search query"
                    },
                    "jurisdiction": {
                        "type": "string",
                        "enum": ["federal", "ontario", "bc", "alberta", "quebec", "manitoba", "saskatchewan"],
                        "description": "Canadian jurisdiction",
                        "default": "federal"
                    },
                    "doc_type": {
                        "type": "string",
                        "enum": ["case", "statute", "regulation", "all"],
                        "description": "Type of legal document"
                    },
                    "date_from": {
                        "type": "string",
                        "description": "Search from date (YYYY-MM-DD)"
                    }
                },
                "required": ["query"]
            }
        }


class SearchLegalUSTool(BaseTool):
    """Search US legal resources via CourtListener API - REAL DATA."""

    def __init__(self):
        super().__init__(
            name="search_legal_us",
            description="Search US legal cases, statutes, and regulations via CourtListener API with real-time data from millions of court opinions",
            category=ToolCategory.RESEARCH
        )

    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_read permission"
            )

        query = parameters.get("query")
        jurisdiction = parameters.get("jurisdiction", "federal")  # federal, state (NY, CA, TX, etc.)
        court = parameters.get("court")  # scotus, ca9, nysd, etc.
        date_filed_after = parameters.get("date_filed_after")
        date_filed_before = parameters.get("date_filed_before")
        limit = parameters.get("limit", 10)

        if not query:
            return ToolResult(
                success=False,
                data=None,
                message="Missing query",
                error="Search query is required"
            )

        try:
            from app.services.courtlistener_service import courtlistener_service

            # Map jurisdiction to court filter if needed
            jurisdiction_map = {
                "federal": "F",
                "state": "S"
            }
            jurisdiction_filter = jurisdiction_map.get(jurisdiction.lower())

            logger.info(f"Searching CourtListener API: query='{query}', court={court}, jurisdiction={jurisdiction}")

            # Search cases using CourtListener - REAL API CALL
            courtlistener_result = await courtlistener_service.search_cases(
                query=query,
                court=court,
                jurisdiction=jurisdiction_filter,
                date_filed_after=date_filed_after,
                date_filed_before=date_filed_before,
                limit=min(limit, 20)
            )

            if not courtlistener_result.get("success"):
                error_msg = courtlistener_result.get("error", "Unknown error")
                return ToolResult(
                    success=False,
                    data=None,
                    message=f"CourtListener API error: {error_msg}",
                    error=error_msg
                )

            # Format results for AI
            results = []
            for case in courtlistener_result.get("cases", []):
                results.append({
                    "type": "case",
                    "title": case.get("case_name", "Unknown"),
                    "citation": ", ".join(case.get("citation", [])) if case.get("citation") else "No citation",
                    "court": case.get("court", "Unknown"),
                    "date": case.get("date_filed", "Unknown"),
                    "jurisdiction": jurisdiction.upper(),
                    "summary": case.get("snippet", "No summary available"),
                    "docket_number": case.get("docket_number", "N/A"),
                    "url": case.get("opinion_url", ""),
                    "case_id": case.get("case_id", ""),
                    "data_source": "CourtListener API (Real-Time)"
                })

            logger.info(f"US legal search completed for {user_id}: Found {len(results)} cases")

            return ToolResult(
                success=True,
                data={
                    "search_id": f"US-LEG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "query": query,
                    "jurisdiction": jurisdiction,
                    "court": court,
                    "results": results,
                    "total_results": courtlistener_result.get("total_results", 0),
                    "results_returned": len(results),
                    "sources": ["CourtListener API - Millions of US Court Opinions"],
                    "searched_at": datetime.now().isoformat(),
                    "data_source": "CourtListener API (Real-Time)"
                },
                message=f"Found {courtlistener_result.get('total_results', 0)} total results, returning {len(results)} cases from CourtListener API"
            )

        except Exception as e:
            logger.error(f"Failed to search US legal cases: {str(e)}")
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to search US legal cases: {str(e)}",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Legal search query (e.g., 'habeas corpus', 'negligence', 'breach of contract')"
                    },
                    "jurisdiction": {
                        "type": "string",
                        "enum": ["federal", "state"],
                        "description": "Jurisdiction to search - federal or state courts",
                        "default": "federal"
                    },
                    "court": {
                        "type": "string",
                        "description": "Specific court identifier (e.g., 'scotus' for Supreme Court, 'ca9' for Ninth Circuit, 'nysd' for Southern District of New York)"
                    },
                    "date_filed_after": {
                        "type": "string",
                        "description": "Filter cases filed after this date (YYYY-MM-DD)"
                    },
                    "date_filed_before": {
                        "type": "string",
                        "description": "Filter cases filed before this date (YYYY-MM-DD)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-20)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }


# ============================================
# RESEARCH PROJECT MANAGEMENT
# ============================================

class CreateResearchProjectTool(BaseTool):
    """Create a new research project."""
    
    def __init__(self):
        super().__init__(
            name="create_research_project",
            description="Create a new research project with organized folder structure for documents",
            category=ToolCategory.RESEARCH
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_write", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_write permission"
            )
        
        project_name = parameters.get("project_name")
        project_type = parameters.get("project_type", "general")
        description = parameters.get("description", "")
        
        if not project_name:
            return ToolResult(
                success=False,
                data=None,
                message="Missing project name",
                error="Project name is required"
            )
        
        # STUBBED: Create project
        project = {
            "project_id": f"PROJ-{random.randint(100000, 999999)}",
            "name": project_name,
            "type": project_type,
            "description": description,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "folder_structure": {
                "root": f"./documents/projects/{project_name.lower().replace(' ', '_')}",
                "subfolders": [
                    "research_notes",
                    "sources",
                    "drafts",
                    "final_documents",
                    "references"
                ]
            },
            "documents": [],
            "collaborators": [],
            "tags": []
        }
        
        logger.info(f"Research project created for {user_id}: {project['project_id']}")
        
        return ToolResult(
            success=True,
            data=project,
            message=f"Research project '{project_name}' created successfully"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Name for the research project"
                    },
                    "project_type": {
                        "type": "string",
                        "enum": ["legal_canada", "legal_us", "business", "market", "general"],
                        "description": "Type of research project",
                        "default": "general"
                    },
                    "description": {
                        "type": "string",
                        "description": "Project description"
                    }
                },
                "required": ["project_name"]
            }
        }


class ListResearchProjectsTool(BaseTool):
    """List all research projects."""
    
    def __init__(self):
        super().__init__(
            name="list_research_projects",
            description="List all research projects with their status and document counts",
            category=ToolCategory.RESEARCH
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_read permission"
            )
        
        project_type = parameters.get("project_type")  # Optional filter
        status = parameters.get("status", "active")
        
        # STUBBED: Mock projects
        projects = [
            {
                "project_id": "PROJ-001",
                "name": "Contract Dispute Research",
                "type": "legal_canada",
                "status": "active",
                "document_count": 12,
                "last_updated": (datetime.now() - timedelta(days=2)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=30)).isoformat()
            },
            {
                "project_id": "PROJ-002",
                "name": "US Tax Implications",
                "type": "legal_us",
                "status": "active",
                "document_count": 8,
                "last_updated": (datetime.now() - timedelta(days=5)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=60)).isoformat()
            },
            {
                "project_id": "PROJ-003",
                "name": "New Venture Business Plan",
                "type": "business",
                "status": "active",
                "document_count": 15,
                "last_updated": datetime.now().isoformat(),
                "created_at": (datetime.now() - timedelta(days=14)).isoformat()
            },
            {
                "project_id": "PROJ-004",
                "name": "Market Expansion Analysis",
                "type": "market",
                "status": "completed",
                "document_count": 20,
                "last_updated": (datetime.now() - timedelta(days=45)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=90)).isoformat()
            }
        ]
        
        # Filter by type
        if project_type:
            projects = [p for p in projects if p["type"] == project_type]
        
        # Filter by status
        if status != "all":
            projects = [p for p in projects if p["status"] == status]
        
        logger.info(f"Listed {len(projects)} research projects for {user_id}")
        
        return ToolResult(
            success=True,
            data={
                "projects": projects,
                "total_count": len(projects),
                "total_documents": sum(p["document_count"] for p in projects)
            },
            message=f"Found {len(projects)} research projects"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "project_type": {
                        "type": "string",
                        "enum": ["legal_canada", "legal_us", "business", "market", "general"],
                        "description": "Filter by project type"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "completed", "archived", "all"],
                        "description": "Filter by status",
                        "default": "active"
                    }
                },
                "required": []
            }
        }


# ============================================
# DOCUMENT MANAGEMENT
# ============================================

class SaveDocumentTool(BaseTool):
    """Save a document to a research project."""
    
    def __init__(self):
        super().__init__(
            name="save_document",
            description="Save a research document, report, or file to a project",
            category=ToolCategory.RESEARCH
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_write", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_write permission"
            )
        
        project_id = parameters.get("project_id")
        document_name = parameters.get("document_name")
        document_type = parameters.get("document_type", "other")
        content = parameters.get("content")
        folder = parameters.get("folder", "drafts")
        
        if not all([project_id, document_name]):
            return ToolResult(
                success=False,
                data=None,
                message="Missing required parameters",
                error="Project ID and document name are required"
            )
        
        # STUBBED: Save document
        document = {
            "document_id": f"DOC-{random.randint(100000, 999999)}",
            "project_id": project_id,
            "name": document_name,
            "type": document_type,
            "folder": folder,
            "path": f"./documents/projects/{project_id}/{folder}/{document_name}",
            "size_kb": random.randint(10, 500),
            "version": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": user_id
        }
        
        logger.info(f"Document saved for {user_id}: {document['document_id']}")
        
        return ToolResult(
            success=True,
            data=document,
            message=f"Document '{document_name}' saved to project"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID to save document to"
                    },
                    "document_name": {
                        "type": "string",
                        "description": "Name for the document"
                    },
                    "document_type": {
                        "type": "string",
                        "enum": ["legal_brief", "business_plan", "research_report", "memo", "contract", "other"],
                        "description": "Type of document",
                        "default": "other"
                    },
                    "content": {
                        "type": "string",
                        "description": "Document content (optional)"
                    },
                    "folder": {
                        "type": "string",
                        "enum": ["research_notes", "sources", "drafts", "final_documents", "references"],
                        "description": "Folder to save in",
                        "default": "drafts"
                    }
                },
                "required": ["project_id", "document_name"]
            }
        }


class ListDocumentsTool(BaseTool):
    """List documents in a project or all projects."""
    
    def __init__(self):
        super().__init__(
            name="list_documents",
            description="List all documents and files with their history",
            category=ToolCategory.RESEARCH
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_read permission"
            )
        
        project_id = parameters.get("project_id")
        document_type = parameters.get("document_type")
        
        # STUBBED: Mock documents
        documents = [
            {
                "document_id": "DOC-001",
                "project_id": "PROJ-001",
                "project_name": "Contract Dispute Research",
                "name": "Case Summary - Smith v. Corp.pdf",
                "type": "legal_brief",
                "folder": "research_notes",
                "size_kb": 245,
                "version": 3,
                "created_at": (datetime.now() - timedelta(days=20)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=2)).isoformat()
            },
            {
                "document_id": "DOC-002",
                "project_id": "PROJ-003",
                "project_name": "New Venture Business Plan",
                "name": "Business Plan v2.docx",
                "type": "business_plan",
                "folder": "drafts",
                "size_kb": 380,
                "version": 2,
                "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "document_id": "DOC-003",
                "project_id": "PROJ-002",
                "project_name": "US Tax Implications",
                "name": "Tax Research Notes.docx",
                "type": "research_report",
                "folder": "research_notes",
                "size_kb": 156,
                "version": 1,
                "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=5)).isoformat()
            },
            {
                "document_id": "DOC-004",
                "project_id": "PROJ-003",
                "project_name": "New Venture Business Plan",
                "name": "Market Analysis Report.xlsx",
                "type": "research_report",
                "folder": "final_documents",
                "size_kb": 520,
                "version": 1,
                "created_at": (datetime.now() - timedelta(days=7)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=3)).isoformat()
            }
        ]
        
        # Filter by project
        if project_id:
            documents = [d for d in documents if d["project_id"] == project_id]
        
        # Filter by type
        if document_type:
            documents = [d for d in documents if d["type"] == document_type]
        
        logger.info(f"Listed {len(documents)} documents for {user_id}")
        
        return ToolResult(
            success=True,
            data={
                "documents": documents,
                "total_count": len(documents),
                "total_size_kb": sum(d["size_kb"] for d in documents)
            },
            message=f"Found {len(documents)} documents"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Filter by project ID"
                    },
                    "document_type": {
                        "type": "string",
                        "enum": ["legal_brief", "business_plan", "research_report", "memo", "contract", "other"],
                        "description": "Filter by document type"
                    }
                },
                "required": []
            }
        }


class GetDocumentHistoryTool(BaseTool):
    """Get version history of a document."""
    
    def __init__(self):
        super().__init__(
            name="get_document_history",
            description="Get version history and changes for a document",
            category=ToolCategory.RESEARCH
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_read permission"
            )
        
        document_id = parameters.get("document_id")
        
        if not document_id:
            return ToolResult(
                success=False,
                data=None,
                message="Missing document ID",
                error="Document ID is required"
            )
        
        # STUBBED: Mock version history
        history = {
            "document_id": document_id,
            "document_name": "Business Plan v2.docx",
            "current_version": 3,
            "versions": [
                {
                    "version": 1,
                    "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
                    "created_by": user_id,
                    "size_kb": 280,
                    "changes": "Initial draft created"
                },
                {
                    "version": 2,
                    "created_at": (datetime.now() - timedelta(days=15)).isoformat(),
                    "created_by": user_id,
                    "size_kb": 350,
                    "changes": "Added market analysis section, updated financial projections"
                },
                {
                    "version": 3,
                    "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
                    "created_by": user_id,
                    "size_kb": 380,
                    "changes": "Final revisions, executive summary updated"
                }
            ]
        }
        
        logger.info(f"Document history retrieved for {user_id}: {document_id}")
        
        return ToolResult(
            success=True,
            data=history,
            message=f"Retrieved {len(history['versions'])} versions for document"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Document ID to get history for"
                    }
                },
                "required": ["document_id"]
            }
        }


# ============================================
# GENERAL RESEARCH TOOLS
# ============================================

class ConductResearchTool(BaseTool):
    """Conduct general research on a topic."""
    
    def __init__(self):
        super().__init__(
            name="conduct_research",
            description="Conduct research on any topic using web search and AI analysis",
            category=ToolCategory.RESEARCH
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_read permission"
            )
        
        topic = parameters.get("topic")
        research_type = parameters.get("research_type", "general")
        depth = parameters.get("depth", "standard")  # quick, standard, comprehensive
        
        if not topic:
            return ToolResult(
                success=False,
                data=None,
                message="Missing topic",
                error="Research topic is required"
            )
        
        # STUBBED: Mock research results
        research = {
            "research_id": f"RES-{random.randint(100000, 999999)}",
            "topic": topic,
            "type": research_type,
            "depth": depth,
            "conducted_at": datetime.now().isoformat(),
            "summary": f"Research on '{topic}' covering key aspects and findings. "
                      f"The analysis includes {random.randint(5, 15)} key points and recommendations.",
            "key_findings": [
                f"Finding 1: {random.choice(['Market trends indicate', 'Analysis shows', 'Research suggests'])} positive outlook",
                f"Finding 2: {random.choice(['Key consideration', 'Important factor', 'Critical element'])} identified",
                f"Finding 3: {random.choice(['Recommendation', 'Suggestion', 'Best practice'])} for implementation"
            ],
            "sources": [
                {"title": f"Source article on {topic}", "url": "https://example.com/1", "credibility": "high"},
                {"title": f"Industry report: {topic}", "url": "https://example.com/2", "credibility": "high"},
                {"title": f"Expert analysis: {topic}", "url": "https://example.com/3", "credibility": "medium"}
            ],
            "related_topics": [
                f"Related topic 1 to {topic}",
                f"Related topic 2 to {topic}"
            ]
        }
        
        logger.info(f"Research conducted for {user_id}: {topic}")
        
        return ToolResult(
            success=True,
            data=research,
            message=f"Research completed on '{topic}'"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to research"
                    },
                    "research_type": {
                        "type": "string",
                        "enum": ["legal", "business", "market", "technical", "general"],
                        "description": "Type of research",
                        "default": "general"
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["quick", "standard", "comprehensive"],
                        "description": "Research depth",
                        "default": "standard"
                    }
                },
                "required": ["topic"]
            }
        }


class GenerateResearchReportTool(BaseTool):
    """Generate a research report."""
    
    def __init__(self):
        super().__init__(
            name="generate_research_report",
            description="Generate a formatted research report from project findings",
            category=ToolCategory.RESEARCH
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_write", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_write permission"
            )
        
        project_id = parameters.get("project_id")
        report_type = parameters.get("report_type", "summary")  # summary, detailed, executive
        format_type = parameters.get("format", "pdf")  # pdf, docx, html
        
        if not project_id:
            return ToolResult(
                success=False,
                data=None,
                message="Missing project ID",
                error="Project ID is required"
            )
        
        # STUBBED: Generate report
        report = {
            "report_id": f"RPT-{random.randint(100000, 999999)}",
            "project_id": project_id,
            "report_type": report_type,
            "format": format_type,
            "generated_at": datetime.now().isoformat(),
            "file_info": {
                "filename": f"research_report_{project_id}_{datetime.now().strftime('%Y%m%d')}.{format_type}",
                "path": f"./exports/research_report_{project_id}.{format_type}",
                "size_kb": random.randint(100, 500)
            },
            "sections": [
                "Executive Summary",
                "Background",
                "Methodology",
                "Key Findings",
                "Analysis",
                "Recommendations",
                "Appendices"
            ],
            "statistics": {
                "pages": random.randint(10, 50),
                "sources_cited": random.randint(5, 30),
                "documents_referenced": random.randint(3, 15)
            }
        }
        
        logger.info(f"Research report generated for {user_id}: {report['report_id']}")
        
        return ToolResult(
            success=True,
            data=report,
            message=f"Research report generated: {report['file_info']['filename']}"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID to generate report for"
                    },
                    "report_type": {
                        "type": "string",
                        "enum": ["summary", "detailed", "executive"],
                        "description": "Type of report",
                        "default": "summary"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pdf", "docx", "html"],
                        "description": "Output format",
                        "default": "pdf"
                    }
                },
                "required": ["project_id"]
            }
        }


# ============================================
# DOCUMENT SUMMARIZATION & LISTING TOOLS
# ============================================

class SummarizeDocumentTool(BaseTool):
    """Summarize an uploaded document using LLM."""

    def __init__(self):
        super().__init__(
            name="summarize_document",
            description="Summarize an uploaded document. Can summarize a specific document by name/ID, or summarize all uploaded documents.",
            category=ToolCategory.RESEARCH
        )

    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_read permission"
            )

        document_name = parameters.get("document_name", "")
        summarize_all = parameters.get("summarize_all", False)

        try:
            from pathlib import Path
            from app.config import settings
            from app.rag.document_loader import DocumentLoader

            docs_dir = Path(settings.DOCUMENTS_DIR) / user_id
            if not docs_dir.exists():
                return ToolResult(
                    success=False,
                    data=None,
                    message="No documents found. Please upload documents first.",
                    error="No documents directory"
                )

            # Find matching documents
            all_files = [f for f in docs_dir.iterdir() if f.is_file() and not f.name.endswith('.meta.json')]
            if not all_files:
                return ToolResult(
                    success=False,
                    data=None,
                    message="No documents found. Please upload documents first.",
                    error="No documents found"
                )

            target_files = []
            if summarize_all:
                target_files = all_files
            elif document_name:
                # Fuzzy match by name
                name_lower = document_name.lower()
                for f in all_files:
                    if name_lower in f.name.lower() or name_lower in f.stem.lower():
                        target_files.append(f)
                if not target_files:
                    # Try matching any file
                    target_files = all_files[:1]
            else:
                # Default: summarize the most recent file
                target_files = sorted(all_files, key=lambda f: f.stat().st_mtime, reverse=True)[:1]

            summaries = []
            loader = DocumentLoader()

            for file_path in target_files[:5]:  # Max 5 docs at once
                try:
                    # Read original filename from metadata
                    import json as _meta_json
                    original_name = file_path.name
                    meta_file = file_path.parent / f"{file_path.stem}.meta.json"
                    if meta_file.exists():
                        try:
                            with open(meta_file, 'r') as mf:
                                _meta = _meta_json.load(mf)
                                original_name = _meta.get('original_filename', file_path.name)
                        except Exception:
                            pass

                    doc_data = await loader.load(str(file_path))
                    text = doc_data['text']
                    metadata = doc_data['metadata']

                    # Truncate for LLM context window
                    max_chars = 8000
                    truncated = text[:max_chars] + ("..." if len(text) > max_chars else "")

                    # Use OpenAI for summarization
                    from app.config import settings as app_settings
                    from openai import AsyncOpenAI

                    client = AsyncOpenAI(api_key=app_settings.OPENAI_API_KEY)
                    response = await client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a document summarizer. Provide a clear, comprehensive summary of the document. Include key points, important details, and main conclusions."},
                            {"role": "user", "content": f"Please summarize this document titled '{metadata.get('filename', 'Unknown')}':\n\n{truncated}"}
                        ],
                        temperature=0.3,
                        max_tokens=1000
                    )
                    summary_text = response.choices[0].message.content

                    summaries.append({
                        "document_id": file_path.stem,
                        "filename": original_name,
                        "format": metadata.get('format', file_path.suffix),
                        "size_bytes": metadata.get('size', file_path.stat().st_size),
                        "summary": summary_text,
                        "word_count": len(text.split()),
                        "pages": metadata.get('pages', None)
                    })
                except Exception as e:
                    logger.error(f"Error summarizing {file_path.name}: {e}")
                    summaries.append({
                        "document_id": file_path.stem,
                        "filename": file_path.name,
                        "summary": f"Error summarizing document: {str(e)}",
                        "error": True
                    })

            return ToolResult(
                success=True,
                data={
                    "summaries": summaries,
                    "total_documents": len(summaries),
                    "downloadable": True
                },
                message=f"Successfully summarized {len(summaries)} document(s)"
            )

        except Exception as e:
            logger.error(f"Summarize document error: {e}")
            return ToolResult(
                success=False,
                data=None,
                message=f"Error: {str(e)}",
                error=str(e)
            )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "document_name": {
                        "type": "string",
                        "description": "Name or partial name of the document to summarize. If empty, summarizes the most recent document."
                    },
                    "summarize_all": {
                        "type": "boolean",
                        "description": "If true, summarize all uploaded documents",
                        "default": False
                    }
                },
                "required": []
            }
        }


class ListUploadedDocsTool(BaseTool):
    """List all documents uploaded by the user."""

    def __init__(self):
        super().__init__(
            name="list_uploaded_documents",
            description="List all documents that the user has uploaded for AI processing and summarization.",
            category=ToolCategory.RESEARCH
        )

    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("research_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have research_read permission"
            )

        try:
            from pathlib import Path
            from app.config import settings

            docs_dir = Path(settings.DOCUMENTS_DIR) / user_id
            if not docs_dir.exists():
                return ToolResult(
                    success=True,
                    data={"documents": [], "total": 0},
                    message="No documents uploaded yet."
                )

            documents = []
            for file_path in docs_dir.iterdir():
                if file_path.is_file() and not file_path.name.endswith('.meta.json'):
                    stat = file_path.stat()
                    # Try reading original filename from metadata
                    import json as _json
                    original_name = file_path.name
                    meta_path = docs_dir / f"{file_path.stem}.meta.json"
                    if meta_path.exists():
                        try:
                            with open(meta_path, 'r') as mf:
                                meta = _json.load(mf)
                                original_name = meta.get('original_filename', file_path.name)
                        except Exception:
                            pass
                    documents.append({
                        "document_id": file_path.stem,
                        "filename": original_name,
                        "format": file_path.suffix.lstrip('.'),
                        "size_bytes": stat.st_size,
                        "size_display": f"{stat.st_size / 1024:.1f} KB" if stat.st_size < 1024 * 1024 else f"{stat.st_size / (1024 * 1024):.2f} MB",
                        "uploaded_at": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "status": "indexed"
                    })

            documents.sort(key=lambda d: d["uploaded_at"], reverse=True)

            return ToolResult(
                success=True,
                data={
                    "documents": documents,
                    "total": len(documents)
                },
                message=f"You have {len(documents)} uploaded document(s)."
            )

        except Exception as e:
            logger.error(f"List documents error: {e}")
            return ToolResult(
                success=False,
                data=None,
                message=f"Error: {str(e)}",
                error=str(e)
            )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }


# ============================================
# RESEARCH TOOLS COLLECTION
# ============================================

class ResearchTools:
    """Collection of all research tools."""
    
    @staticmethod
    def get_all_tools() -> list[BaseTool]:
        """Get all research tools."""
        return [
            # Legal Research (US - CourtListener API)
            SearchLegalUSTool(),  # Search cases with real-time CourtListener data
            GetLegalCaseDetailsTool(),  # Get detailed case information
            SearchLegalDocketsTool(),  # Search court dockets and filings

            # Legal Research (Canada - CanLII)
            SearchLegalCanadaTool(),

            # Project Management
            CreateResearchProjectTool(),
            ListResearchProjectsTool(),

            # Document Management
            SaveDocumentTool(),
            ListDocumentsTool(),
            GetDocumentHistoryTool(),

            # Document Summarization & Upload Management
            SummarizeDocumentTool(),
            ListUploadedDocsTool(),

            # General Research
            ConductResearchTool(),
            GenerateResearchReportTool()
        ]
    
    @staticmethod
    def get_schemas() -> list[Dict[str, Any]]:
        """Get all research tool schemas."""
        return [tool.get_schema() for tool in ResearchTools.get_all_tools()]
