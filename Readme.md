# AN INTELLIGENT AI - Complete Project Documentation

---

## Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [Features Overview](#2-features-overview)
3. [System Requirements](#3-system-requirements)
4. [Project Structure](#4-project-structure)
5. [Installation Guide](#5-installation-guide)
6. [Configuration](#6-configuration)
7. [Running the Application](#7-running-the-application)
8. [Using the Application](#8-using-the-application)
9. [API Integrations](#9-api-integrations)
10. [Database Information](#10-database-information)
11. [User Management](#11-user-management)
12. [Troubleshooting](#12-troubleshooting)
13. [Security](#13-security)
14. [Future Enhancements](#14-future-enhancements)

---

## 1. What Is This Project?

**AN INTELLIGENT AI** is a smart personal assistant application that combines multiple services into one platform:

- **Banking** - Connect and view your real bank accounts
- **Travel** - Search real-time flights with actual prices
- **Stocks** - Track live stock market prices
- **Legal Research** - Search millions of US court cases
- **AI Chat** - Talk naturally to get things done

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    YOU (User)                            │
│         Talk naturally or use forms                      │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              AN INTELLIGENT AI                           │
│         Understands what you need                        │
└─────────────────────────┬───────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │  Plaid   │   │ Amadeus  │   │  Alpha   │
    │ Banking  │   │ Flights  │   │ Vantage  │
    └──────────┘   └──────────┘   └──────────┘
          │               │               │
          ▼               ▼               ▼
    Real Bank       Real Flight      Real Stock
    Data            Prices           Prices
```

---

## 2. Features Overview

### 2.1 Banking Module
| Feature | Description |
|---------|-------------|
| Connect Banks | Link real bank accounts (Chase, BoA, Wells Fargo, etc.) |
| View Balances | See all account balances in one place |
| Transactions | View transaction history |
| Export | Export data to Excel |
| Reports | Generate accountant reports |

### 2.2 Travel Module
| Feature | Description |
|---------|-------------|
| Flight Search | Search 500+ airlines worldwide |
| Real Prices | See actual ticket prices |
| Availability | Check seat availability |
| Multiple Options | Compare direct and connecting flights |

### 2.3 Stocks Module
| Feature | Description |
|---------|-------------|
| Live Quotes | Real-time stock prices |
| Portfolio | Track your investments |
| Search | Find any stock by symbol |
| History | View price history |

### 2.4 Legal Research Module
| Feature | Description |
|---------|-------------|
| Case Search | Search millions of US court opinions |
| Filters | Filter by court, jurisdiction, date |
| Full Text | Read complete case details |
| Citations | View legal citations |

### 2.5 AI Chat
| Feature | Description |
|---------|-------------|
| Natural Language | Talk like you would to a person |
| Multi-Module | Access all features through chat |
| Context Aware | Remembers conversation history |
| Smart Responses | Formatted, easy-to-read answers |

---

## 3. System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| Operating System | Windows 10+, macOS 10.15+, or Linux |
| Python | Version 3.10 or higher |
| Node.js | Version 18 or higher |
| MySQL | Version 8.0 or higher |
| RAM | 4 GB minimum, 8 GB recommended |
| Storage | 2 GB free space |
| Internet | Required for API calls |

### Check Your Versions

Open terminal and run:

```bash
# Check Python
python3 --version
# Should show: Python 3.10+

# Check Node.js
node --version
# Should show: v18+

# Check npm
npm --version
# Should show: 9+

# Check MySQL
mysql --version
# Should show: mysql Ver 8.0+
```

---

## 4. Project Structure

```
AN-INTELLIGENT-AI/
│
├── backend/                      # Python Backend Server
│   ├── app/
│   │   ├── auth/                # Authentication
│   │   │   ├── dependencies.py  # Auth middleware
│   │   │   ├── security.py      # JWT tokens
│   │   │   └── service.py       # Auth logic
│   │   │
│   │   ├── database/            # Database
│   │   │   ├── database.py      # DB connection
│   │   │   └── models.py        # Data models
│   │   │
│   │   ├── routers/             # API Endpoints
│   │   │   ├── auth.py          # Login/Register
│   │   │   ├── chat.py          # AI Chat
│   │   │   ├── plaid.py         # Banking
│   │   │   ├── stocks.py        # Stock market
│   │   │   └── tools.py         # Tool invocation
│   │   │
│   │   ├── services/            # External APIs
│   │   │   ├── amadeus_service.py       # Flight search
│   │   │   ├── plaid_service.py         # Banking
│   │   │   ├── alpha_vantage_service.py # Stocks
│   │   │   ├── courtlistener_service.py # Legal research
│   │   │   └── chat_service.py          # AI processing
│   │   │
│   │   ├── tools/               # AI Tools
│   │   │   ├── banking_tools.py
│   │   │   ├── travel_tools.py
│   │   │   ├── stock_tools.py
│   │   │   ├── research_tools.py
│   │   │   └── tool_registry.py
│   │   │
│   │   ├── prompts/             # AI Prompts
│   │   │   ├── banking.py
│   │   │   ├── travel.py
│   │   │   ├── research.py
│   │   │   └── base_system.py
│   │   │
│   │   ├── config.py            # Configuration
│   │   ├── schemas.py           # Data schemas
│   │   └── main.py              # App entry point
│   │
│   ├── .env                     # Environment variables (API keys)
│   ├── .env.example             # Example environment file
│   ├── requirements.txt         # Python dependencies
│   └── venv/                    # Python virtual environment
│
├── frontend/                    # React Frontend
│   ├── public/
│   │   ├── index.html          # Main HTML
│   │   └── manifest.json       # PWA config
│   │
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   │   ├── BankConnect.jsx
│   │   │   └── PlaidLink.jsx
│   │   │
│   │   ├── layouts/            # Page layouts
│   │   │   ├── AuthLayout.jsx
│   │   │   └── DashboardLayout.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── auth/           # Login pages
│   │   │   │   ├── Login.jsx
│   │   │   │   ├── Register.jsx
│   │   │   │   └── ForgotPassword.jsx
│   │   │   │
│   │   │   └── dashboard/      # Main pages
│   │   │       ├── Dashboard.jsx
│   │   │       ├── Banking.jsx
│   │   │       ├── Travel.jsx
│   │   │       ├── Stocks.jsx
│   │   │       ├── Research.jsx
│   │   │       └── Chat.jsx
│   │   │
│   │   ├── store/              # State management
│   │   │   └── authStore.js
│   │   │
│   │   ├── App.jsx             # Main app component
│   │   └── index.js            # Entry point
│   │
│   ├── package.json            # Node dependencies
│   └── tailwind.config.js      # Styling config
│
├── PROJECT_COMPLETE_DOCUMENTATION.md  # This file
├── PLAID_PRODUCTION_GUIDE.md          # Banking setup guide
└── apikeys.md                         # API keys reference
```

---

## 5. Installation Guide

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd Ai-Assistance-

# Or extract the downloaded ZIP file
```

### Step 2: Set Up MySQL Database

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE ai_assistant;

# Create user (optional, can use root)
CREATE USER 'aiuser'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ai_assistant.* TO 'aiuser'@'localhost';
FLUSH PRIVILEGES;

# Exit MySQL
exit
```

### Step 3: Set Up Backend

```bash
# Go to backend folder
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Set Up Frontend

```bash
# Go to frontend folder
cd ../frontend

# Install dependencies
npm install
```

---

## 6. Configuration

### Step 1: Create Environment File

```bash
cd backend
cp .env.example .env
```

### Step 2: Edit .env File

Open `backend/.env` and fill in your values:

```bash
# ===========================================
# DATABASE CONFIGURATION
# ===========================================
DATABASE_URL=mysql+aiomysql://root:your_password@localhost:3306/ai_assistant

# ===========================================
# SECURITY
# ===========================================
SECRET_KEY=your-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ===========================================
# AI PROVIDERS (Choose one or more)
# ===========================================
# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Google Gemini
GOOGLE_API_KEY=your-google-api-key

# ===========================================
# EXTERNAL APIS
# ===========================================
# Plaid (Banking)
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
PLAID_ENV=sandbox

# Amadeus (Travel)
AMADEUS_API_KEY=your-amadeus-api-key
AMADEUS_API_SECRET=your-amadeus-api-secret
AMADEUS_TEST_MODE=true

# Alpha Vantage (Stocks)
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key

# CourtListener (Legal Research)
COURTLISTENER_API_TOKEN=your-courtlistener-token
```

### Where to Get API Keys

| Service | Sign Up URL | Cost |
|---------|-------------|------|
| OpenAI | https://platform.openai.com | Pay per use |
| Anthropic | https://console.anthropic.com | Pay per use |
| Google AI | https://makersuite.google.com | Free tier available |
| Plaid | https://dashboard.plaid.com | Free sandbox |
| Amadeus | https://developers.amadeus.com | Free tier (2000 calls/month) |
| Alpha Vantage | https://www.alphavantage.co | Free (25 calls/day) |
| CourtListener | https://www.courtlistener.com/api | Free |

---

## 7. Running the Application

### Method 1: Run Both Servers Manually

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Method 2: Quick Start Commands

**Linux/Mac:**
```bash
# Start Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000 &

# Start Frontend
cd frontend && npm start &
```

### Verify Servers Are Running

| Server | URL | Expected Response |
|--------|-----|-------------------|
| Backend Health | http://localhost:8000/health | `{"status":"healthy"}` |
| Backend Docs | http://localhost:8000/docs | API documentation |
| Frontend | http://localhost:3000 | Login page |

### Stop Servers

```bash
# Find and kill processes
pkill -f uvicorn
pkill -f "npm start"

# Or press Ctrl+C in each terminal
```

---

## 8. Using the Application

### 8.1 First Time Setup

1. **Open Browser:** Go to http://localhost:3000
2. **Register:** Click "Create Account" and fill in your details
3. **Login:** Use your email and password
4. **Explore:** You'll see the Dashboard with all modules

### 8.2 Banking Module

**Connect a Bank (Sandbox Mode):**
1. Go to Banking page
2. Click "Connect Bank Account"
3. In sandbox mode, use these test credentials:
   - Bank: Select any bank
   - Username: `user_good`
   - Password: `pass_good`
4. Your test accounts will appear

**View Transactions:**
- Click on any account to see transactions
- Use filters to search by date or category

**AI Chat Example:**
```
You: "Show me my bank accounts"
AI: Lists all your connected accounts with balances

You: "What did I spend on food last month?"
AI: Shows food-related transactions and total
```

### 8.3 Travel Module

**Search Flights:**
1. Go to Travel page
2. Enter:
   - From: Airport code (e.g., `JFK`, `LAX`, `ORD`)
   - To: Airport code
   - Date: Select departure date
3. Click "Search Flights"
4. Results show real prices from Amadeus

**Airport Codes Examples:**
| City | Code |
|------|------|
| New York | JFK, LGA, EWR |
| Los Angeles | LAX |
| Chicago | ORD |
| Miami | MIA |
| London | LHR |
| Dubai | DXB |

**AI Chat Example:**
```
You: "Find flights from New York to Los Angeles on January 25"
AI: Shows real-time flight options with prices
```

### 8.4 Stocks Module

**Check Stock Price:**
1. Go to Stocks page
2. Enter stock symbol (e.g., `AAPL`, `GOOGL`, `MSFT`)
3. Click "Get Quote"
4. See real-time price data

**AI Chat Example:**
```
You: "What's the current price of Apple stock?"
AI: Shows AAPL current price, change, and daily range

You: "How is Tesla doing today?"
AI: Shows TSLA stock information
```

### 8.5 Legal Research Module

**Search Cases:**
1. Go to Research page
2. Enter search terms (e.g., "contract breach", "negligence")
3. Optionally select jurisdiction and court
4. Click "Search Cases"
5. Results show real US court cases

**AI Chat Example:**
```
You: "Find cases about medical malpractice in California"
AI: Shows relevant court cases with summaries
```

### 8.6 AI Chat (General)

The chat can access all modules. Just describe what you need:

```
You: "Show my bank balance"
You: "Search flights to Miami"
You: "What's Google stock at?"
You: "Find cases about breach of contract"
```

---

## 9. API Integrations

### 9.1 Plaid (Banking)

**Purpose:** Connect real bank accounts

**Environments:**
| Environment | Use Case | Data |
|-------------|----------|------|
| Sandbox | Testing | Fake data |
| Development | Testing with real banks | Real data (free, 100 connections) |
| Production | Live application | Real data (paid) |

**Current Setup:** Sandbox (test mode)

**To Use Real Banks:** See `PLAID_PRODUCTION_GUIDE.md`

### 9.2 Amadeus (Travel)

**Purpose:** Real-time flight search

**Coverage:**
- 500+ airlines worldwide
- Real prices and availability
- Global Distribution System (GDS) data

**Rate Limits:**
- Free tier: 2,000 calls/month
- Test environment for development

**Current Setup:** Test mode (real data, test environment)

### 9.3 Alpha Vantage (Stocks)

**Purpose:** Stock market data

**Coverage:**
- US stock markets
- Real-time quotes
- Historical data

**Rate Limits:**
- Free tier: 25 calls/day
- Premium: 500+ calls/day

### 9.4 CourtListener (Legal)

**Purpose:** US legal case research

**Coverage:**
- Millions of US court opinions
- Supreme Court, Federal, State courts
- Full text and citations

**Rate Limits:**
- Free: 5,000 requests/hour with API token

**API Version:** v4 (current)

### 9.5 AI Providers

**Supported:**
| Provider | Model | Purpose |
|----------|-------|---------|
| OpenAI | GPT-4 | Primary AI |
| Anthropic | Claude | Alternative |
| Google | Gemini | Backup |

**Current Default:** OpenAI (configurable in .env)

---

## 10. Database Information

### Database Type
MySQL 8.0+

### Main Tables

**users**
- Stores user accounts
- Fields: id, email, password_hash, name, is_verified, is_active

**user_permissions**
- Stores module access permissions
- Fields: user_id, module, permission_type, granted

**plaid_accounts**
- Stores connected bank accounts
- Fields: user_id, access_token, item_id, institution_name

**chat_sessions**
- Stores conversation history
- Fields: user_id, session_id, messages, created_at

### Database Connection

Configured in `.env`:
```
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/ai_assistant
```

### Reset Database

```bash
# Login to MySQL
mysql -u root -p

# Drop and recreate database
DROP DATABASE ai_assistant;
CREATE DATABASE ai_assistant;
exit

# Restart backend (tables auto-create)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

---

## 11. User Management

### Default Users

The system may have test users. Check with:
```sql
SELECT email, is_verified, is_active FROM users;
```

### Create New User

1. Go to http://localhost:3000/register
2. Fill in: Name, Email, Password
3. Click "Create Account"
4. User is automatically verified in development

### User Permissions

Each user needs permissions for modules:

| Module | Permission Types |
|--------|-----------------|
| banking | banking_read, banking_write |
| travel | travel_read, travel_write |
| stocks | stocks_read, stocks_write |
| research | research_read, research_write |
| chat | chat_read |

**Add Permissions Manually (SQL):**
```sql
-- Get user ID first
SELECT id FROM users WHERE email = 'user@example.com';

-- Add travel permission (replace USER_ID)
INSERT INTO user_permissions (user_id, module, permission_type, granted, granted_at, granted_by)
VALUES (USER_ID, 'travel', 'travel_read', 1, NOW(), 'admin');
```

---

## 12. Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError`
```bash
# Solution: Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**Error:** `Database connection failed`
```bash
# Solution: Check MySQL is running
sudo systemctl start mysql

# Check credentials in .env
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/ai_assistant
```

### Frontend Won't Start

**Error:** `npm ERR!`
```bash
# Solution: Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error:** `Port 3000 already in use`
```bash
# Solution: Kill existing process
lsof -ti:3000 | xargs kill -9
npm start
```

### API Errors

**Error:** `401 Unauthorized`
- User not logged in or token expired
- Solution: Log out and log back in

**Error:** `403 Forbidden`
- User doesn't have permission
- Solution: Add permissions (see User Management section)

**Error:** `No flights found`
- Use 3-letter airport codes (JFK, not "New York")
- Use future dates
- Check internet connection

**Error:** `CourtListener API error: 403`
- API version issue (should be v4)
- Check COURTLISTENER_API_TOKEN in .env

### Check Logs

**Backend logs:**
```bash
cd backend
tail -f backend.log
```

**Frontend logs:**
- Open browser Developer Tools (F12)
- Go to Console tab

---

## 13. Security

### Password Security
- Passwords are hashed using bcrypt
- Never stored in plain text
- Minimum 8 characters required

### API Token Security
- JWT tokens expire after 60 minutes
- Tokens stored in browser memory (not localStorage)
- HTTPS recommended for production

### API Keys
- All API keys stored in `.env` file
- Never commit `.env` to git
- Use `.env.example` as template

### Bank Data Security
- Plaid handles bank credentials
- We never see your bank password
- Access tokens are encrypted
- Read-only access (cannot make transfers)

### Best Practices
1. Use strong passwords
2. Don't share API keys
3. Keep `.env` file private
4. Use HTTPS in production
5. Regularly rotate API keys

---

## 14. Future Enhancements

### Planned Features

**Phase 1:**
- [ ] Hotel booking integration
- [ ] Car rental search
- [ ] Multi-city flight search
- [ ] Price alerts

**Phase 2:**
- [ ] Mobile app (React Native)
- [ ] Voice commands
- [ ] Email notifications
- [ ] Calendar integration

**Phase 3:**
- [ ] Cryptocurrency tracking
- [ ] International transfers
- [ ] Tax document generation
- [ ] Budget recommendations

### Technical Improvements
- [ ] Response caching
- [ ] Real-time notifications (WebSockets)
- [ ] Offline mode
- [ ] Multi-language support

---

## Quick Reference Card

### Start Application
```bash
# Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend && npm start
```

### URLs
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### Test Credentials (Sandbox)
| Service | Username | Password |
|---------|----------|----------|
| Plaid Bank | user_good | pass_good |

### Common Airport Codes
| City | Code |
|------|------|
| New York JFK | JFK |
| Los Angeles | LAX |
| Chicago | ORD |
| Miami | MIA |
| San Francisco | SFO |
| London Heathrow | LHR |

### Common Stock Symbols
| Company | Symbol |
|---------|--------|
| Apple | AAPL |
| Google | GOOGL |
| Microsoft | MSFT |
| Amazon | AMZN |
| Tesla | TSLA |

---

## Support

### Documentation Files
- `PROJECT_COMPLETE_DOCUMENTATION.md` - This file
- `PLAID_PRODUCTION_GUIDE.md` - Real banking setup
- `apikeys.md` - API keys reference

### External Documentation
- Plaid: https://plaid.com/docs/
- Amadeus: https://developers.amadeus.com/self-service
- Alpha Vantage: https://www.alphavantage.co/documentation/
- CourtListener: https://www.courtlistener.com/api/

---

**Project:** AN INTELLIGENT AI
**Version:** 1.0
**Last Updated:** January 2026
