# CourtListener API Setup Guide

## ✅ Integration Status

**Backend Integration:** COMPLETE
- ✅ CourtListener service implemented ([courtlistener_service.py](app/services/courtlistener_service.py))
- ✅ Legal research tools created (search_legal_us, get_legal_case_details, search_legal_dockets)
- ✅ Tools registered in ToolRegistry
- ✅ Research module prompt updated
- ✅ User permissions configured (all 7 users have research_read and research_write)
- ✅ Permission checks working correctly

**API Status:** Requires Authentication Token

---

## 🔑 How to Get CourtListener API Token

CourtListener provides **FREE** access to millions of US court opinions with an API token.

### Step 1: Create Free Account

1. Go to https://www.courtlistener.com
2. Click "Sign Up" in top-right corner
3. Fill in:
   - Email address
   - Username
   - Password
4. Verify your email address

### Step 2: Get API Token

1. Log in to CourtListener
2. Go to https://www.courtlistener.com/api/rest-info/
3. Scroll to "Authentication" section
4. Click "View your API token" or "Get API token"
5. Copy the token (format: `Token abc123def456...`)

### Step 3: Add Token to Application

**Option A: Environment Variable (Recommended)**

Add to [backend/.env](backend/.env):
```bash
# CourtListener API (Legal Research)
COURTLISTENER_API_TOKEN=your_token_here
```

**Option B: Direct in Code**

Edit [backend/app/services/courtlistener_service.py](backend/app/services/courtlistener_service.py):
```python
# Replace this line (around line 286):
courtlistener_service = CourtListenerService(api_token=None)

# With:
courtlistener_service = CourtListenerService(api_token="your_token_here")
```

### Step 4: Restart Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📊 API Limits

### Free Tier (with API token)
- **5,000 requests per hour** - Very generous!
- **No cost** - Completely free
- **Full access** to all court opinions
- **No credit card required**

### Without Token
- 100 requests per day (limited)
- Less suitable for production use

### Coverage
- **Millions** of US court opinions
- Supreme Court (all opinions)
- Circuit Courts (all 13 federal circuits)
- District Courts
- State Supreme Courts
- PACER federal court dockets

---

## 🧪 Test the Integration

After adding your API token, run the test suite:

```bash
cd backend
source venv/bin/activate
python test_legal_research.py
```

**Expected Output:**
```
✅ PASS - CourtListener Service
✅ PASS - SearchLegalUSTool
✅ PASS - SearchLegalDocketsTool
✅ PASS - Permission Check

Results: 4/4 tests passed
🎉 ALL TESTS PASSED! CourtListener API integration is working!
```

---

## 💬 How to Use via AI Chat

Once the API token is configured, users can search US case law through natural language:

### Example Queries

**User:** "Find US cases about habeas corpus"

**AI will:**
1. Call `search_legal_us` tool
2. CourtListener API searches millions of opinions
3. Returns real cases with citations
4. Formats response with case names, courts, dates

**User:** "Search for Fourth Amendment cases"

**AI will:**
1. Extract search terms
2. Call CourtListener API
3. Return actual Supreme Court and Circuit Court opinions
4. Include links to full opinion text

**User:** "Get details on case ID 12345"

**AI will:**
1. Call `get_legal_case_details` tool
2. Retrieve full opinion text
3. Show authorship, court info, download links

---

## 🔧 Troubleshooting

### Error: "Anonymous users don't have permission"
**Cause:** No API token configured
**Fix:** Follow steps above to get and add API token

### Error: "Rate limit exceeded"
**Cause:** Over 5,000 requests in one hour
**Fix:** Wait an hour or implement caching

### Error: "Invalid API token"
**Cause:** Wrong token format
**Fix:** Ensure token includes "Token " prefix (e.g., `Token abc123...`)

---

## 📚 What Data You Get

### Case Search Results
```json
{
  "case_name": "Smith v. United States",
  "citation": ["550 U.S. 124", "127 S. Ct. 1696"],
  "court": "U.S. Supreme Court",
  "date_filed": "2007-05-21",
  "docket_number": "06-8273",
  "snippet": "Fourth Amendment search and seizure...",
  "opinion_url": "https://www.courtlistener.com/opinion/145678/",
  "case_id": 145678
}
```

### Data Source
- **Primary Source:** CourtListener database
- **PACER Integration:** Federal court records
- **Updated:** Continuously (new opinions added as decided)
- **Quality:** Official court opinions, properly cited

---

## 🎯 Use Cases

### 1. Prototype Demo
Show real-time legal research capabilities:
- Search for "negligence" → Get hundreds of real cases
- Search for "employment discrimination" → See actual federal cases
- Demonstrate AI understanding legal queries

### 2. Client Legal Research
Client asks: "Find cases similar to my mother's situation"
- AI searches CourtListener
- Returns relevant precedents
- Analyzes case holdings
- Suggests legal strategies

### 3. Document Analysis (Future)
When client uploads mother's case documents:
- AI extracts legal issues
- Searches CourtListener for similar cases
- Finds favorable precedents
- Generates legal research memo

---

## 📈 Success Metrics

**Current Test Results:**
- ✅ Permission system: Working
- ⚠️  API calls: Need token (expected)
- ✅ Tools registered: All 3 legal tools
- ✅ User permissions: All 7 users configured

**After Token Configuration:**
- Real-time case search from millions of opinions
- Full opinion text retrieval
- Docket search and case tracking
- AI-powered legal Q&A

---

## 🆓 Cost Analysis

### CourtListener API
- **Free forever** with API token
- **5,000 requests/hour** = 120,000/day free
- **No credit card** required
- **No hidden fees**

### Comparison
- **Westlaw:** $100-500/month (enterprise)
- **LexisNexis:** $300-500/month
- **Fastcase:** $65/month
- **CourtListener:** **$0/month** ✅

### ROI
Using CourtListener saves $780-$6,000 per year compared to paid legal research services.

---

## 🚀 Next Steps

1. **Get API Token** (5 minutes)
   - Sign up at courtlistener.com
   - Copy your token

2. **Add to Application** (1 minute)
   - Update .env or service file
   - Restart backend

3. **Test Integration** (2 minutes)
   - Run test_legal_research.py
   - Verify 4/4 tests pass

4. **Demo to Client** (15 minutes)
   - Show real-time case search
   - Demonstrate AI legal Q&A
   - Explain FREE data source

**Total Setup Time: ~10 minutes**

---

## 📞 Support

**CourtListener Issues:**
- Documentation: https://www.courtlistener.com/api/rest-info/
- GitHub: https://github.com/freelawproject/courtlistener
- Contact: info@courtlistener.com

**Integration Issues:**
- Check [LEGAL_RESEARCH_API_GUIDE.md](LEGAL_RESEARCH_API_GUIDE.md)
- Review [test_legal_research.py](test_legal_research.py) output
- Verify permissions: `python verify_research_permissions.py`

---

## ✅ Checklist

- [ ] Create free CourtListener account
- [ ] Get API token
- [ ] Add token to .env or service file
- [ ] Restart backend server
- [ ] Run test suite (should pass 4/4)
- [ ] Test via AI chat ("Find US cases about...")
- [ ] Demo to client

**Once complete, you'll have FREE access to millions of US court opinions through AI chat!** 🎉
