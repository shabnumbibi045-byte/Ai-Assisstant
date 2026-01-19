"""Knowledge Base Loader - Loads domain-specific knowledge into RAG system."""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

class KnowledgeBaseLoader:
    """Loads knowledge base documents into the system."""

    KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent.parent / "knowledge_base"

    DOMAIN_KNOWLEDGE = {
        "banking": {
            "files": ["multi_country_banking_guide.md"],
            "description": "Multi-country banking operations, currency exchange, regulations"
        },
        "stocks": {
            "files": ["investment_analysis_guide.md"],
            "description": "Stock analysis, portfolio management, investment strategies"
        },
        "travel": {
            "files": ["travel_booking_guide.md"],
            "description": "Flight and hotel booking, travel optimization, tips"
        },
        "research": {
            "files": ["legal_research_guide.md"],
            "description": "Legal research for Canada and US, case law, statutes"
        }
    }

    @classmethod
    def get_knowledge_context(cls, query: str, domain: str = None) -> str:
        """
        Get relevant knowledge base context for a query.

        This is a simplified version that returns key knowledge for demo.
        In production, this would use embeddings and vector search.
        """

        # Domain detection from query
        if not domain:
            query_lower = query.lower()
            if any(word in query_lower for word in ['bank', 'account', 'transfer', 'currency', 'balance']):
                domain = 'banking'
            elif any(word in query_lower for word in ['stock', 'invest', 'portfolio', 'trade', 'market']):
                domain = 'stocks'
            elif any(word in query_lower for word in ['flight', 'hotel', 'travel', 'booking', 'trip']):
                domain = 'travel'
            elif any(word in query_lower for word in ['legal', 'law', 'case', 'statute', 'court']):
                domain = 'research'

        if not domain:
            return ""

        # Get knowledge file
        domain_info = cls.DOMAIN_KNOWLEDGE.get(domain, {})
        files = domain_info.get('files', [])

        if not files:
            return ""

        # Read the knowledge file
        knowledge_path = cls.KNOWLEDGE_BASE_DIR / domain / files[0]

        try:
            if knowledge_path.exists():
                with open(knowledge_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract relevant sections (simplified - in production use embeddings)
                sections = cls._extract_relevant_sections(content, query)
                return sections
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")

        return ""

    @classmethod
    def _extract_relevant_sections(cls, content: str, query: str, max_chars: int = 4000) -> str:
        """Extract most relevant sections from knowledge base."""

        # Split into sections (by headers)
        sections = []
        current_section = []

        for line in content.split('\n'):
            if line.startswith('##') and current_section:
                sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)

        if current_section:
            sections.append('\n'.join(current_section))

        # Score sections by relevance (simple keyword matching)
        query_words = set(query.lower().split())
        scored_sections = []

        for section in sections:
            section_words = set(section.lower().split())
            overlap = len(query_words & section_words)
            if overlap > 0:
                scored_sections.append((overlap, section))

        # Sort by relevance and combine top sections
        scored_sections.sort(reverse=True, key=lambda x: x[0])

        result = []
        total_chars = 0

        for score, section in scored_sections:
            if total_chars + len(section) > max_chars:
                break
            result.append(section)
            total_chars += len(section)

        return '\n\n'.join(result)

    @classmethod
    def get_banking_context(cls) -> str:
        """Get banking knowledge summary."""
        return """
        BANKING KNOWLEDGE SUMMARY:

        ⚠️ CRITICAL: User must connect their bank account via Plaid to access real banking data.
        DO NOT provide example or mock banking data. ALWAYS use the banking tools to fetch real-time data.

        Multi-Country Banking Support:
        - Canada (CA): CAD currency
        - USA (US): USD currency
        - Kenya (KE): KES currency

        Currency Exchange (General Market Rates - Not User-Specific):
        - USD to CAD: ~1.35
        - USD to KES: ~129.50
        - Best transfer methods: Wise (0.5-2% fees), bank wires ($25-50)

        Transaction Categories (for categorization):
        - Operating Expenses, Marketing, Professional Services
        - Personal: Housing, Transportation, Food, Healthcare

        Compliance Requirements:
        - Canada: FINTRAC requirements, $10K reporting threshold
        - USA: BSA compliance, SAR filing
        - Kenya: CBK oversight, Anti-Money Laundering Act

        REMINDER: This is general banking knowledge. For user's actual accounts, balances, and transactions,
        you MUST call the banking tools which fetch real data from Plaid. Never invent account details.
        """

    @classmethod
    def get_stocks_context(cls) -> str:
        """Get stocks knowledge summary."""
        return """
        STOCK ANALYSIS KNOWLEDGE SUMMARY:

        Fundamental Analysis:
        - P/E Ratio: <15 undervalued, 15-25 fair, >25 growth/overvalued
        - Profit Margins: Software 70-90%, Retail 20-40%
        - Current Ratio: 1.5-3.0 healthy
        - Debt-to-Equity: <0.5 conservative, 0.5-1.5 moderate

        Technical Indicators:
        - RSI: >70 overbought, <30 oversold
        - Moving Averages: Golden Cross (bullish), Death Cross (bearish)
        - MACD: Cross above signal = buy, below = sell

        Portfolio Management:
        - Conservative: 60% Bonds, 30% Large-cap, 10% Cash
        - Aggressive: 70% Stocks, 20% Growth, 10% Cash/Bonds
        - Diversification: Max 20-25% per sector, 5% per stock

        Risk Management:
        - Position sizing based on 2% account risk
        - Stop-loss: 7-10% below purchase
        - Risk-reward minimum: 1:2
        """

    @classmethod
    def get_travel_context(cls) -> str:
        """Get travel knowledge summary."""
        return """
        TRAVEL BOOKING KNOWLEDGE SUMMARY:

        Best Booking Times:
        - Domestic Flights: 1-3 months ahead, Tuesday/Wednesday bookings
        - International: 2-8 months ahead, avoid weekends
        - Hotels: 2-3 months for popular destinations

        Price Optimization:
        - Flight comparison: Google Flights, Skyscanner, Hopper
        - Hotel loyalty: Marriott Bonvoy, Hilton Honors, Hyatt (best value)
        - Credit card insurance: Trip cancellation, lost luggage

        Airline Alliances:
        - Star Alliance: United, Air Canada, Lufthansa (26 airlines)
        - OneWorld: American, British Airways, Qatar (13 airlines)
        - SkyTeam: Delta, Air France-KLM (19 airlines)

        Travel Tips:
        - TSA PreCheck/Global Entry for faster security
        - Priority Pass for 1,300+ airport lounges
        - Travel insurance: 4-10% of trip cost
        - Visa requirements: Check 4-6 weeks before travel
        """

    @classmethod
    def get_research_context(cls) -> str:
        """Get legal research knowledge summary."""
        return """
        LEGAL RESEARCH KNOWLEDGE SUMMARY:

        Canadian Courts:
        - Supreme Court of Canada (SCC): Final appeal, binding on all
        - Federal Court: IP, maritime, immigration
        - Provincial: Court of Appeal (highest), Superior Court, Provincial Court
        - Free research: CanLII.org

        US Courts:
        - Supreme Court (SCOTUS): Final federal authority
        - Circuit Courts: 13 circuits, appeals
        - District Courts: 94 districts, trial courts
        - Free research: Google Scholar, Justia, Cornell LII

        Business Law:
        - Canada: CBCA (federal corp), OBCA (Ontario), 25% Canadian directors
        - USA: C Corp (double tax), S Corp (pass-through), LLC (flexible)
        - Director liability: Business judgment rule, due diligence defense

        Tax Rates:
        - Canada Corporate: 15% federal + provincial (~26.5% Ontario)
        - Canada Personal: 20-53.5% progressive
        - USA Corporate: 21% federal flat
        - USA Personal: 10-37% progressive + state
        """

    @classmethod
    async def initialize_knowledge_base(cls):
        """Initialize knowledge base on startup."""
        logger.info("Initializing knowledge base...")

        for domain, info in cls.DOMAIN_KNOWLEDGE.items():
            domain_path = cls.KNOWLEDGE_BASE_DIR / domain
            if domain_path.exists():
                file_count = len(list(domain_path.glob("*.md")))
                logger.info(f"Knowledge base ready: {domain} ({file_count} files) - {info['description']}")
            else:
                logger.warning(f"Knowledge base directory not found: {domain_path}")

        logger.info("Knowledge base initialization complete")

    @classmethod
    def enhance_prompt_with_knowledge(cls, user_message: str, system_context: str = "") -> tuple[str, str]:
        """
        Enhance chat prompt with relevant knowledge base context.

        Returns: (enhanced_system_prompt, knowledge_used)
        """

        # Detect domain and get relevant knowledge
        knowledge_context = cls.get_knowledge_context(user_message)

        if not knowledge_context:
            # If no specific domain detected, provide general context
            knowledge_context = """
            AVAILABLE EXPERTISE:
            - Banking: Multi-country operations (CA, US, KE), currency exchange, compliance
            - Stocks: Portfolio analysis, fundamental/technical analysis, risk management
            - Travel: Flight/hotel booking optimization, loyalty programs, cost savings
            - Legal: Canadian & US case law, statutes, corporate/business law

            Use /api/v1/banking, /api/v1/stocks, /api/v1/travel, /api/v1/research endpoints for detailed data.
            """

        enhanced_system = f"""{system_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 KNOWLEDGE BASE CONTEXT (MUST USE THIS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{knowledge_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  CRITICAL INSTRUCTIONS - MUST FOLLOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **MANDATORY FOR BANKING**: You MUST call banking tools to fetch REAL Plaid data
2. **NO MOCK DATA**: NEVER use example bank names, account numbers, or balances unless returned from real tools
3. **CHECK CONNECTION FIRST**: Before answering banking questions, verify user has connected their bank via Plaid
4. **USE REAL TOOL DATA**: Only reference actual data returned from tool calls, not examples from knowledge base
5. **BE DETAILED**: Provide comprehensive answers with sections, bullets, and specific examples FROM REAL DATA
6. **FORMAT WELL**: Use **bold**, bullets, and clear sections for readability
7. **BE CONVERSATIONAL**: Sound natural and helpful, not robotic
8. **PROVIDE VALUE**: Give actionable recommendations and next steps

❌ DO NOT FOR BANKING:
- Use example bank names like "TD Canada Trust", "RBC", "Chase", "Bank of America" unless they're from real Plaid data
- Fabricate account numbers, balances, or transactions
- Provide banking information without calling the tools first
- Use "demo data" or "example accounts" in banking responses

✅ CORRECT BANKING FLOW:
1. User asks about banking → Call list_bank_accounts tool
2. If NO_BANK_CONNECTED error → Tell user to connect bank via Plaid in the Banking page
3. If accounts found → Use REAL data from tool response to answer
4. Format response with actual account names, real balances, real transactions from tools

For non-banking domains (stocks, travel, research), you can use the knowledge base information as before.

NOW ANSWER THE USER'S QUESTION USING THE KNOWLEDGE BASE ABOVE:
"""

        return enhanced_system, knowledge_context[:500]  # Return first 500 chars as summary


# Global instance
knowledge_loader = KnowledgeBaseLoader()
