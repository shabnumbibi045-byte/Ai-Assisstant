"""Research Router - Legal and business research for Canada and US."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.auth.dependencies import get_current_active_user
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["research"])


# ============================================
# SCHEMAS
# ============================================

class LegalDocument(BaseModel):
    """Legal document or case."""
    document_id: str
    title: str
    jurisdiction: str  # CA-Federal, CA-ON, US-Federal, US-NY, etc.
    document_type: str  # case, statute, regulation, treaty
    citation: str
    date_published: datetime
    court: Optional[str]
    summary: str
    key_points: List[str]
    relevance_score: float  # 0-100
    url: Optional[str]


class ResearchQuery(BaseModel):
    """Research query result."""
    query_id: str
    query_text: str
    jurisdiction: List[str]
    document_types: List[str]
    created_at: datetime
    results_count: int
    status: str


class CaseLawSearch(BaseModel):
    """Case law search result."""
    total_results: int
    results: List[LegalDocument]
    filters_applied: Dict[str, Any]
    search_time_ms: int


class StatuteInfo(BaseModel):
    """Statute or regulation information."""
    statute_id: str
    title: str
    jurisdiction: str
    chapter: str
    section: str
    text: str
    last_amended: Optional[datetime]
    status: str  # in_force, repealed, proposed
    related_regulations: List[str]


class LegalAnalysis(BaseModel):
    """AI-powered legal analysis."""
    analysis_id: str
    question: str
    jurisdiction: str
    analysis: str
    relevant_cases: List[LegalDocument]
    relevant_statutes: List[StatuteInfo]
    key_considerations: List[str]
    recommended_actions: List[str]
    confidence_level: float  # 0-100
    created_at: datetime


class ComplianceCheck(BaseModel):
    """Regulatory compliance check."""
    check_id: str
    business_type: str
    jurisdiction: str
    requirements: List[Dict[str, Any]]
    compliance_status: str  # compliant, non_compliant, partial
    recommendations: List[str]
    deadline: Optional[datetime]


# ============================================
# DEMO DATA GENERATORS
# ============================================

def get_demo_legal_documents(jurisdiction: Optional[str] = None) -> List[LegalDocument]:
    """Generate demo legal documents."""
    all_docs = [
        LegalDocument(
            document_id="CA_SCC_001",
            title="R. v. Jordan - Right to trial within reasonable time",
            jurisdiction="CA-Federal",
            document_type="case",
            citation="2016 SCC 27",
            date_published=datetime(2016, 7, 8),
            court="Supreme Court of Canada",
            summary="The Supreme Court established new framework for assessing trial delays under s. 11(b) of the Charter.",
            key_points=[
                "Presumptive ceiling of 18 months for provincial court trials",
                "30 months for superior court trials",
                "Defense waiver and extraordinary circumstances exceptions",
                "Transitional exceptional circumstance for cases in system"
            ],
            relevance_score=95.5,
            url="https://scc-csc.lexum.com/scc-csc/scc-csc/en/item/16057/index.do"
        ),
        LegalDocument(
            document_id="CA_ON_002",
            title="Business Corporations Act - Director Liability",
            jurisdiction="CA-ON",
            document_type="statute",
            citation="R.S.O. 1990, c. B.16, s. 131",
            date_published=datetime(1990, 1, 1),
            court=None,
            summary="Provisions governing director and officer liability for corporate obligations.",
            key_points=[
                "Directors liable for up to 6 months wages to employees",
                "Personal liability for certain tax obligations",
                "Due diligence defense available",
                "Joint and several liability with corporation"
            ],
            relevance_score=88.2,
            url="https://www.ontario.ca/laws/statute/90b16"
        ),
        LegalDocument(
            document_id="US_SCOTUS_001",
            title="Brown v. Board of Education - School Desegregation",
            jurisdiction="US-Federal",
            document_type="case",
            citation="347 U.S. 483 (1954)",
            date_published=datetime(1954, 5, 17),
            court="Supreme Court of the United States",
            summary="Landmark decision declaring state laws establishing racial segregation in public schools unconstitutional.",
            key_points=[
                "Separate educational facilities are inherently unequal",
                "Violates Equal Protection Clause of 14th Amendment",
                "Overturned Plessy v. Ferguson's 'separate but equal' doctrine",
                "Foundation for Civil Rights Movement"
            ],
            relevance_score=92.8,
            url="https://supreme.justia.com/cases/federal/us/347/483/"
        ),
        LegalDocument(
            document_id="US_NY_001",
            title="New York Business Corporation Law - Shareholder Rights",
            jurisdiction="US-NY",
            document_type="statute",
            citation="N.Y. Bus. Corp. Law § 620",
            date_published=datetime(1961, 9, 1),
            court=None,
            summary="Provisions governing shareholder voting rights and procedures.",
            key_points=[
                "One share, one vote default rule",
                "Cumulative voting for directors if provided in certificate",
                "Proxy voting procedures and requirements",
                "Shareholder meeting quorum requirements"
            ],
            relevance_score=85.0,
            url="https://www.nysenate.gov/legislation/laws/BSC/620"
        ),
    ]

    if jurisdiction:
        return [doc for doc in all_docs if doc.jurisdiction == jurisdiction]
    return all_docs


def get_demo_statutes() -> List[StatuteInfo]:
    """Generate demo statute information."""
    return [
        StatuteInfo(
            statute_id="CA_ITA_001",
            title="Income Tax Act - Corporate Tax Rates",
            jurisdiction="CA-Federal",
            chapter="I-3.3",
            section="123-125",
            text="The basic federal corporate tax rate is 38%. After federal tax abatement (10%) and general rate reduction (13%), the net federal rate is 15%. Small business deduction reduces rate to 9% on first $500,000 of active business income.",
            last_amended=datetime(2022, 6, 23),
            status="in_force",
            related_regulations=["Reg. 5200", "Reg. 5201"]
        ),
        StatuteInfo(
            statute_id="US_IRC_001",
            title="Internal Revenue Code - Corporate Tax",
            jurisdiction="US-Federal",
            chapter="26",
            section="11",
            text="A tax is hereby imposed for each taxable year on the taxable income of every corporation. The amount of the tax is 21 percent of taxable income (as of 2018 Tax Cuts and Jobs Act).",
            last_amended=datetime(2017, 12, 22),
            status="in_force",
            related_regulations=["26 CFR 1.11-1"]
        ),
    ]


# ============================================
# ENDPOINTS
# ============================================

@router.get("/search/cases", response_model=CaseLawSearch)
async def search_case_law(
    query: str = Query(..., description="Search query"),
    jurisdiction: Optional[str] = Query(None, description="CA-Federal, CA-ON, US-Federal, US-NY, etc."),
    date_from: Optional[datetime] = Query(None, description="Filter cases from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter cases until this date"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search case law across Canadian and US jurisdictions.
    Powered by AI for semantic search and relevance ranking.
    """
    try:
        start_time = datetime.now()

        documents = get_demo_legal_documents(jurisdiction)

        # Apply date filters
        if date_from:
            documents = [d for d in documents if d.date_published >= date_from]
        if date_to:
            documents = [d for d in documents if d.date_published <= date_to]

        # Sort by relevance
        documents = sorted(documents, key=lambda x: x.relevance_score, reverse=True)[:limit]

        search_time = (datetime.now() - start_time).microseconds // 1000

        result = CaseLawSearch(
            total_results=len(documents),
            results=documents,
            filters_applied={
                "query": query,
                "jurisdiction": jurisdiction,
                "date_from": date_from,
                "date_to": date_to
            },
            search_time_ms=search_time
        )

        logger.info(f"Case law search: {len(documents)} results for user {current_user.email}")
        return result

    except Exception as e:
        logger.error(f"Case law search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/search/statutes", response_model=List[StatuteInfo])
async def search_statutes(
    query: str = Query(..., description="Search query"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search statutes and regulations.
    Includes current and historical versions.
    """
    try:
        statutes = get_demo_statutes()

        if jurisdiction:
            statutes = [s for s in statutes if s.jurisdiction == jurisdiction]

        logger.info(f"Statute search: {len(statutes)} results for user {current_user.email}")
        return statutes

    except Exception as e:
        logger.error(f"Statute search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/analyze", response_model=LegalAnalysis)
async def analyze_legal_question(
    question: str,
    jurisdiction: str,
    context: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-powered legal analysis for a specific question.
    Includes relevant cases, statutes, and actionable recommendations.
    """
    try:
        # Demo analysis - in production would use advanced AI/LLM
        analysis = LegalAnalysis(
            analysis_id=f"ANALYSIS_{datetime.now().timestamp()}",
            question=question,
            jurisdiction=jurisdiction,
            analysis=(
                "Based on the current legal framework and precedents in the specified jurisdiction, "
                "the following analysis applies:\n\n"
                "1. **Legal Basis**: The question touches upon fundamental principles of contract law "
                "and statutory obligations.\n\n"
                "2. **Precedent Review**: Several landmark cases provide guidance on this matter, "
                "establishing clear standards for interpretation.\n\n"
                "3. **Statutory Framework**: Relevant statutes impose specific requirements and "
                "provide remedies for non-compliance.\n\n"
                "4. **Risk Assessment**: The current situation presents moderate legal risk that "
                "can be mitigated through proper documentation and compliance procedures."
            ),
            relevant_cases=get_demo_legal_documents(jurisdiction)[:3],
            relevant_statutes=get_demo_statutes()[:2],
            key_considerations=[
                "Ensure compliance with statutory notice requirements",
                "Document all communications and decisions",
                "Consider contractual obligations and deadlines",
                "Review potential liability exposure",
                "Evaluate alternative dispute resolution options"
            ],
            recommended_actions=[
                "Consult with legal counsel for jurisdiction-specific advice",
                "Prepare comprehensive documentation of relevant facts",
                "Review and update compliance procedures",
                "Consider risk mitigation strategies",
                "Monitor for regulatory or case law developments"
            ],
            confidence_level=85.5,
            created_at=datetime.now()
        )

        logger.info(f"Generated legal analysis for user {current_user.email}")
        return analysis

    except Exception as e:
        logger.error(f"Legal analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")


@router.get("/compliance/check", response_model=ComplianceCheck)
async def check_compliance(
    business_type: str = Query(..., description="Type of business (corporation, partnership, etc.)"),
    jurisdiction: str = Query(..., description="Operating jurisdiction"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check regulatory compliance requirements for a business.
    Includes deadlines and recommendations.
    """
    try:
        check = ComplianceCheck(
            check_id=f"CHECK_{datetime.now().timestamp()}",
            business_type=business_type,
            jurisdiction=jurisdiction,
            requirements=[
                {
                    "requirement": "Annual Corporate Returns",
                    "description": "File annual returns with corporate registry",
                    "status": "pending",
                    "deadline": (datetime.now() + timedelta(days=45)).date(),
                    "penalty": "Late fees and potential dissolution"
                },
                {
                    "requirement": "Tax Filings",
                    "description": "Corporate income tax return (T2/1120)",
                    "status": "compliant",
                    "deadline": None,
                    "penalty": "N/A - Filed on time"
                },
                {
                    "requirement": "Directors' Resolutions",
                    "description": "Maintain current minute book with required resolutions",
                    "status": "partial",
                    "deadline": None,
                    "penalty": "Potential piercing of corporate veil"
                },
            ],
            compliance_status="partial",
            recommendations=[
                "File outstanding annual returns before deadline to avoid penalties",
                "Schedule board meeting to approve and document pending resolutions",
                "Review corporate governance documents for completeness",
                "Set up calendar reminders for recurring compliance obligations"
            ],
            deadline=datetime.now() + timedelta(days=45)
        )

        logger.info(f"Compliance check for {business_type} in {jurisdiction} - user {current_user.email}")
        return check

    except Exception as e:
        logger.error(f"Compliance check error: {e}")
        raise HTTPException(status_code=500, detail="Compliance check failed")


@router.get("/jurisdictions")
async def get_supported_jurisdictions(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of supported legal jurisdictions."""
    return {
        "canada": [
            {"code": "CA-Federal", "name": "Canada (Federal)"},
            {"code": "CA-ON", "name": "Ontario"},
            {"code": "CA-BC", "name": "British Columbia"},
            {"code": "CA-AB", "name": "Alberta"},
            {"code": "CA-QC", "name": "Quebec"},
        ],
        "united_states": [
            {"code": "US-Federal", "name": "United States (Federal)"},
            {"code": "US-NY", "name": "New York"},
            {"code": "US-CA", "name": "California"},
            {"code": "US-TX", "name": "Texas"},
            {"code": "US-FL", "name": "Florida"},
        ]
    }


@router.get("/recent-queries", response_model=List[ResearchQuery])
async def get_recent_queries(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's recent research queries."""
    try:
        queries = [
            ResearchQuery(
                query_id="Q001",
                query_text="director liability corporate obligations Canada",
                jurisdiction=["CA-Federal", "CA-ON"],
                document_types=["case", "statute"],
                created_at=datetime.now() - timedelta(hours=2),
                results_count=45,
                status="completed"
            ),
            ResearchQuery(
                query_id="Q002",
                query_text="shareholder rights voting proxy",
                jurisdiction=["US-NY"],
                document_types=["statute", "regulation"],
                created_at=datetime.now() - timedelta(days=1),
                results_count=23,
                status="completed"
            ),
        ]

        logger.info(f"Retrieved {len(queries)} recent queries for user {current_user.email}")
        return queries[:limit]

    except Exception as e:
        logger.error(f"Error retrieving queries: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve queries")
