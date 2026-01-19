"""
Test CourtListener API Integration
Tests legal research tools with real API calls.
"""

import asyncio
import sys
from app.services.courtlistener_service import courtlistener_service
from app.tools.research_tools import SearchLegalUSTool, GetLegalCaseDetailsTool, SearchLegalDocketsTool


async def test_courtlistener_service():
    """Test CourtListener service directly."""
    print("=" * 80)
    print("TEST 1: CourtListener Service - Search Cases")
    print("=" * 80)
    print()

    # Test case search
    result = await courtlistener_service.search_cases(
        query="habeas corpus",
        jurisdiction="F",  # Federal
        limit=5
    )

    if result.get("success"):
        print(f"✅ Search successful!")
        print(f"📊 Total results: {result.get('total_results', 0)}")
        print(f"📄 Results returned: {result.get('results_returned', 0)}")
        print()

        if result.get("cases"):
            print("First case:")
            case = result["cases"][0]
            print(f"  📋 Case Name: {case.get('case_name', 'Unknown')}")
            print(f"  📜 Citation: {', '.join(case.get('citation', []))}")
            print(f"  ⚖️  Court: {case.get('court', 'Unknown')}")
            print(f"  📅 Date Filed: {case.get('date_filed', 'Unknown')}")
            print(f"  🔗 URL: {case.get('opinion_url', 'N/A')}")
            print()
        return True
    else:
        print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
        return False


async def test_search_legal_us_tool():
    """Test SearchLegalUSTool."""
    print("=" * 80)
    print("TEST 2: SearchLegalUSTool - Real Tool Execution")
    print("=" * 80)
    print()

    tool = SearchLegalUSTool()

    # Test with proper permissions
    permissions = {
        "research_read": True,
        "research_write": True
    }

    result = await tool.execute(
        user_id="test_user",
        parameters={
            "query": "Fourth Amendment search seizure",
            "jurisdiction": "federal",
            "limit": 3
        },
        permissions=permissions
    )

    if result.success:
        print(f"✅ Tool execution successful!")
        print(f"📊 Message: {result.message}")
        print()

        if result.data and result.data.get("results"):
            print(f"Cases found: {len(result.data['results'])}")
            for i, case in enumerate(result.data["results"][:2], 1):
                print(f"\n{i}. {case.get('title', 'Unknown')}")
                print(f"   Citation: {case.get('citation', 'N/A')}")
                print(f"   Court: {case.get('court', 'Unknown')}")
                print(f"   Date: {case.get('date', 'Unknown')}")
                print(f"   Source: {case.get('data_source', 'Unknown')}")
        print()
        return True
    else:
        print(f"❌ Tool execution failed: {result.message}")
        print(f"   Error: {result.error}")
        return False


async def test_search_legal_dockets_tool():
    """Test SearchLegalDocketsTool."""
    print("=" * 80)
    print("TEST 3: SearchLegalDocketsTool - Docket Search")
    print("=" * 80)
    print()

    tool = SearchLegalDocketsTool()

    permissions = {
        "research_read": True
    }

    result = await tool.execute(
        user_id="test_user",
        parameters={
            "query": "employment discrimination",
            "limit": 3
        },
        permissions=permissions
    )

    if result.success:
        print(f"✅ Docket search successful!")
        print(f"📊 Message: {result.message}")
        print()

        if result.data and result.data.get("dockets"):
            print(f"Dockets found: {len(result.data['dockets'])}")
            for i, docket in enumerate(result.data["dockets"][:2], 1):
                print(f"\n{i}. {docket.get('case_name', 'Unknown')}")
                print(f"   Docket #: {docket.get('docket_number', 'N/A')}")
                print(f"   Court: {docket.get('court', 'Unknown')}")
                print(f"   Filed: {docket.get('date_filed', 'Unknown')}")
        print()
        return True
    else:
        print(f"❌ Docket search failed: {result.message}")
        return False


async def test_permission_check():
    """Test permission checking."""
    print("=" * 80)
    print("TEST 4: Permission Checking")
    print("=" * 80)
    print()

    tool = SearchLegalUSTool()

    # Test without permission
    result = await tool.execute(
        user_id="test_user",
        parameters={"query": "test"},
        permissions={}  # No permissions
    )

    if not result.success and "Permission denied" in result.message:
        print("✅ Permission check working correctly!")
        print(f"   Message: {result.message}")
        print()
        return True
    else:
        print("❌ Permission check failed - should have denied access")
        return False


async def run_all_tests():
    """Run all tests."""
    print("\n")
    print("*" * 80)
    print("COURTLISTENER API INTEGRATION TEST SUITE")
    print("*" * 80)
    print()

    tests = [
        ("CourtListener Service", test_courtlistener_service),
        ("SearchLegalUSTool", test_search_legal_us_tool),
        ("SearchLegalDocketsTool", test_search_legal_dockets_tool),
        ("Permission Check", test_permission_check)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

        print()

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")
    print()

    if passed == total:
        print("🎉 ALL TESTS PASSED! CourtListener API integration is working!")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")

    print("=" * 80)
    print()

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
