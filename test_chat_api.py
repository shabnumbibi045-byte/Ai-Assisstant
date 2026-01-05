#!/usr/bin/env python3
"""
Direct test of the Chat API to verify knowledge base integration.
This bypasses authentication for testing purposes.
"""

import asyncio
import sys
sys.path.insert(0, '/home/ali/Desktop/Ai-Assistance-/backend')

from app.services.chat_service import ChatService
from app.schemas import ChatRequest

async def test_chat():
    """Test chat service with various queries."""

    chat_service = ChatService()

    test_queries = [
        {
            "query": "What are the best Canadian banks for business?",
            "domain": "Banking"
        },
        {
            "query": "How do I analyze stocks using P/E ratio?",
            "domain": "Stocks"
        },
        {
            "query": "When should I book flights to Tokyo?",
            "domain": "Travel"
        },
        {
            "query": "What are corporate tax rates in Canada?",
            "domain": "Legal/Tax"
        }
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test['domain']}")
        print(f"{'='*80}")
        print(f"Query: {test['query']}")
        print(f"{'-'*80}\n")

        request = ChatRequest(
            user_id="test_user",
            session_id="test_session",
            message=test['query'],
            use_tools=False,  # Disable tools for this test
            use_rag=False
        )

        try:
            response = await chat_service.process_message(request)

            print("RESPONSE:")
            print(response.response)
            print(f"\n{'-'*80}")
            print(f"Tokens used: {response.tokens_used}")
            print(f"Sources: {len(response.sources)} knowledge base sources")

            # Check quality
            if len(response.response) > 200:
                print("✅ Response is detailed (>200 chars)")
            else:
                print("❌ Response is too short (<200 chars)")

            if response.tokens_used > 3500:
                print("✅ Knowledge base is being used (high token count)")
            else:
                print("⚠️  Knowledge base might not be used (low token count)")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

        print("\n")

if __name__ == "__main__":
    print("="*80)
    print("AI CHAT KNOWLEDGE BASE TEST")
    print("="*80)
    print("\nThis test verifies that the AI chat is using the knowledge base properly.")
    print("Each response should be detailed, specific, and include facts from the KB.\n")

    asyncio.run(test_chat())

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nIf all tests show ✅ and responses are detailed, the system is working!")
