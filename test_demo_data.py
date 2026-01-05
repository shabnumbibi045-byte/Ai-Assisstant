#!/usr/bin/env python3
"""Test demo data integration."""

import sys
sys.path.insert(0, '/home/ali/Desktop/Ai-Assistance-/backend')

from app.services.demo_data_service import demo_data_service

print("="*80)
print("DEMO DATA SERVICE TEST")
print("="*80)

# Test Banking
print("\n1. BANKING DATA:")
print("-"*80)
accounts = demo_data_service.get_demo_bank_accounts()
print(f"Found {len(accounts)} accounts")
for acc in accounts[:2]:
    print(f"  - {acc['bank_name']} {acc['account_type']}: {acc['currency']} {acc['balance']:,.2f}")

# Test Stocks
print("\n2. STOCK PORTFOLIO DATA:")
print("-"*80)
portfolio = demo_data_service.get_demo_stock_portfolio()
print(f"Total Value: ${portfolio['total_value']:,.2f}")
print(f"Total Gain/Loss: ${portfolio['total_gain_loss']:,.2f} ({portfolio['total_gain_loss_percent']:.2f}%)")
print(f"Holdings: {len(portfolio['holdings'])} stocks")

# Test Query Summaries
print("\n3. QUERY-BASED SUMMARIES:")
print("-"*80)

queries = [
    "What are my bank balances?",
    "Show me my stock portfolio",
    "Find flights to Tokyo"
]

for query in queries:
    print(f"\nQuery: '{query}'")
    summary = demo_data_service.get_summary_for_query(query)
    if summary:
        print(f"Summary length: {len(summary)} characters")
        print(f"Preview: {summary[:200]}...")
    else:
        print("No summary generated")

print("\n" + "="*80)
print("✅ Demo Data Service is working!")
print("="*80)
