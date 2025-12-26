# Salim Rana AI Assistant - Backend

**Comprehensive AI Assistant for Banking, Stocks, Travel & Research**

A production-grade FastAPI backend built specifically for Salim Rana's requirements:
- 🏦 **Multi-Country Banking** - Canada, USA, Kenya with Excel exports for accountant
- 📈 **Stock Portfolio Management** - Trading account monitoring with QuickBooks reports
- ✈️ **Travel Search** - FareCompare, Expedia, Priceline VIP Platinum, Skyscanner
- ⚖️ **Legal Research** - Canada (CanLII) and US (CourtListener) research
- 📁 **Document Management** - File history and version tracking
- 🎤 **Voice Commands** - Speech-to-text and text-to-speech support

---

## 🎯 Features Overview

### 🏦 Multi-Country Banking

**Supported Countries:**
- 🇨🇦 Canada (CAD) - TD, RBC, Scotiabank, BMO, CIBC
- 🇺🇸 United States (USD) - Chase, Bank of America, Wells Fargo, Citi
- 🇰🇪 Kenya (KES) - KCB, Equity Bank, Co-operative Bank

**Capabilities:**
- Daily balance summaries across all accounts
- Transaction history and categorization
- Weekly Excel exports for accountant
- QuickBooks-compatible formats
- Email reports directly to accountant
- Add new accounts anytime via Plaid

**Sample Commands:**
```
"What are my bank balances today?"
"Show me all my transactions from last week"
"Export my banking data for the accountant"
"Add my new Chase account"
```

### 📈 Stock Portfolio Management

**Supported Brokers:**
- Alpaca Trading
- Interactive Brokers
- TD Ameritrade (planned)

**Capabilities:**
- Daily portfolio summaries
- Real-time stock quotes
- Transaction history (buys, sells, dividends)
- Realized/unrealized gains tracking
- Excel exports for accountant
- Tax reporting support

**Sample Commands:**
```
"How are my stocks doing today?"
"What's the current price of NVDA?"
"Export my stock transactions for the accountant"
"Show my realized gains this year"
```

### ✈️ Travel Search with VIP Benefits

**Search Providers:**
- FareCompare - Price comparison
- Expedia - Bundle deals
- **Priceline VIP Platinum** - 8% flights, 10% hotels discount
- Skyscanner - Comprehensive search

**Capabilities:**
- Multi-provider simultaneous search
- Continuous price monitoring (every 30 min)
- Price drop alerts
- VIP Platinum benefits auto-applied
- Trip planning with flights + hotels + cars
- Best value recommendations

**VIP Platinum Benefits:**
| Category | Discount |
|----------|----------|
| Flights | 8% off Express Deals |
| Hotels | 10% off + room upgrades |
| Cars | Priority service + free upgrades |
| Bundles | Additional 5% on packages |

**Sample Commands:**
```
"Find me flights to Miami next month"
"Set up price monitoring for that flight"
"Search hotels in Miami with my VIP rate"
"Plan my whole trip to Vancouver"
```

### ⚖️ Legal Research

**Canada (CanLII):**
- Supreme Court of Canada
- Federal Court
- All Provincial/Territorial Courts
- Administrative Tribunals
- Statutes and Regulations

**United States (CourtListener):**
- Supreme Court
- Circuit Courts of Appeals
- District Courts
- State Courts
- PACER Records

**Capabilities:**
- Case law search by keywords, citation, parties
- Statute and regulation search
- Research project management
- Document version control
- Report generation (PDF, DOCX)

**Sample Commands:**
```
"Research Canadian privacy law for businesses"
"Find US cases about employment discrimination"
"Create a research project for the Smith matter"
"Generate a report on my findings"
```

### 📁 Document Management

**Features:**
- Research project organization
- Folder structure (drafts, final, reference, notes)
- Automatic version tracking
- Document history
- Multiple formats support

### 🎤 Voice Commands

**Capabilities:**
- Speech-to-text (Whisper)
- Text-to-speech (ElevenLabs)
- Natural language command processing
- Intent detection for all modules

---

## 🏗️ Architecture

```
/backend
  /app
    /llm              # LLM providers (OpenAI, Anthropic, Gemini)
    /memory           # Hybrid memory (short-term, long-term, vector)
    /prompts          # Module-specific AI prompts
    /rag              # Document retrieval pipeline
    /tools            # Function calling tools
      banking_tools.py    # Multi-country banking
      stock_tools.py      # Portfolio management
      travel_tools.py     # Multi-provider travel
      research_tools.py   # Legal research & docs
    /database         # SQLAlchemy models
    /routers          # FastAPI endpoints
      chat.py             # Chat interface
      voice.py            # Voice commands
      tools.py            # Tool invocation
    /services         # Business logic
      chat_service.py     # Chat orchestration
      export_service.py   # Excel/PDF generation
    config.py         # Configuration
    schemas.py        # Pydantic models
    main.py           # FastAPI app
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- API Keys (see Configuration)

### Installation

1. **Clone and Navigate**
   ```bash
   cd backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the Server**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access API Docs**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## ⚙️ Configuration

### Required API Keys

Create a `.env` file with the following:

```env
# LLM Providers (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Banking (Plaid)
PLAID_CLIENT_ID=...
PLAID_SECRET=...
PLAID_ENV=sandbox  # sandbox, development, production

# Stocks
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
ALPHA_VANTAGE_API_KEY=...

# Travel
AMADEUS_API_KEY=...
AMADEUS_API_SECRET=...
PRICELINE_API_KEY=...
PRICELINE_VIP_ID=...
EXPEDIA_API_KEY=...
SKYSCANNER_API_KEY=...

# Legal Research
CANLII_API_KEY=...
COURTLISTENER_API_KEY=...

# Voice
WHISPER_MODEL=base  # tiny, base, small, medium, large
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...

# Accountant
ACCOUNTANT_EMAIL=accountant@example.com

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/ai_assistant
```

### Banking Countries

Default configuration supports:
```python
BANKING_COUNTRIES = ["CA", "US", "KE"]
```

To add more countries, update `config.py`.

---

## 📡 API Endpoints

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/` | Send message to AI |
| GET | `/chat/history/{session_id}` | Get chat history |
| DELETE | `/chat/session/{session_id}` | Clear session |

### Banking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tools/invoke` | Invoke banking tools |

Banking Tools:
- `list_bank_accounts` - List all accounts
- `get_balance` - Get account balances
- `get_daily_balance_summary` - Daily summary
- `list_transactions` - Transaction history
- `export_transactions_to_excel` - Excel export
- `generate_accountant_report` - Weekly report

### Stocks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tools/invoke` | Invoke stock tools |

Stock Tools:
- `list_trading_accounts` - List accounts
- `get_portfolio_summary` - Portfolio view
- `get_daily_portfolio_summary` - Daily summary
- `get_stock_quote` - Real-time quotes
- `export_portfolio_to_excel` - Excel export

### Travel
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tools/invoke` | Invoke travel tools |

Travel Tools:
- `search_flights` - Multi-provider search
- `set_flight_price_alert` - Price monitoring
- `search_hotels` - Hotel search with VIP
- `create_trip_plan` - Trip planning

### Research
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tools/invoke` | Invoke research tools |

Research Tools:
- `search_legal_canada` - Canadian legal search
- `search_legal_us` - US legal search
- `create_research_project` - New project
- `save_document` - Save document
- `generate_research_report` - Create report

### Voice
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/voice/transcribe` | Speech to text |
| POST | `/voice/command` | Process voice command |
| POST | `/voice/tts` | Text to speech |

---

## 📊 Weekly Accountant Reports

The system can automatically generate weekly reports for your accountant:

### Banking Report
- All transactions across Canada, US, Kenya
- Categorized and formatted for QuickBooks
- Currency conversions to USD
- Summary totals by account and country

### Stock Report
- All buy/sell transactions
- Dividend income
- Realized gains/losses
- Cost basis tracking

### Automated Email
Reports can be emailed directly to your accountant:
```
"Generate my weekly report and email it to my accountant"
```

---

## 🔐 Security

### Data Protection
- All account numbers masked (****1234)
- API keys stored securely in environment
- No sensitive data in logs

### Transaction Safety
- All payments require explicit confirmation
- Two-factor authentication supported
- Large transactions flagged for review

### Compliance
- PIPEDA compliant (Canada)
- CCPA compliant (US)
- Data Protection Act compliant (Kenya)

---

## 🛠️ Adding New Accounts

### Bank Accounts
1. Say "Add my new bank account"
2. Specify country (Canada, US, or Kenya)
3. Follow Plaid link to authenticate
4. Account connected automatically

### Trading Accounts
1. Say "Add my trading account"
2. Specify broker (Alpaca, Interactive Brokers)
3. Follow OAuth link to authenticate
4. Account syncs automatically

---

## 🤖 Sample Conversations

### Daily Check-in
```
User: "Good morning, give me my daily summary"

AI: Here's your daily summary for March 15, 2025:

🏦 BANKING
├─ Canada: CAD $63,456.00
├─ USA: USD $33,765.43
├─ Kenya: KES 802,457.00
└─ Total (USD): $103,456.78

📈 STOCKS
├─ Total Value: $124,580.13
├─ Day Change: +$802.45 (+0.65%)
└─ YTD Return: +14.14%

✈️ TRAVEL ALERTS
└─ Toronto→Miami dropped to $385! (Was $450)
```

### Accountant Export
```
User: "Export everything for my accountant"

AI: I'll generate your weekly reports:

📊 Banking Transactions Export
├─ Period: Mar 8-15, 2025
├─ Transactions: 47
├─ Countries: CA, US, KE
└─ File: banking_weekly_20250315.xlsx

📈 Stock Transactions Export
├─ Period: Mar 8-15, 2025
├─ Transactions: 12
├─ Realized Gain: +$1,234.56
└─ File: stocks_weekly_20250315.xlsx

Email to accountant@example.com? [Yes/No]
```

---

## 📞 Support

For issues or feature requests:
- Create an issue in the repository
- Contact the development team

---

## 📜 License

Proprietary - Built for Salim Rana

---

*Built with ❤️ using FastAPI, Python, and AI*
