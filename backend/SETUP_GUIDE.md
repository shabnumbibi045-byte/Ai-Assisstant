# AnIntelligentAI Backend - Setup & Run Guide

## ✅ What Has Been Built

### Complete Production-Ready Backend with:

1. **LLM Provider Layer** (`/app/llm/`)
   - ✅ Base provider abstraction
   - ✅ OpenAI integration (GPT-4, embeddings)
   - ✅ Anthropic Claude integration
   - ✅ Google Gemini integration
   - ✅ Provider factory with caching
   - ✅ Retry logic and error handling
   - ✅ Token usage tracking

2. **Memory System** (`/app/memory/`)
   - ✅ Short-term memory (Redis/in-memory)
   - ✅ Long-term memory (PostgreSQL)
   - ✅ Vector memory (Qdrant)
   - ✅ Memory orchestrator
   - ✅ Conversation history management
   - ✅ User facts storage

3. **Prompt Engineering** (`/app/prompts/`)
   - ✅ Base system prompt
   - ✅ Banking module prompt
   - ✅ Travel module prompt
   - ✅ Research module prompt
   - ✅ Communication module prompt
   - ✅ Stocks module prompt

4. **RAG Pipeline** (`/app/rag/`)
   - ✅ Document loader (PDF, DOCX, TXT, MD)
   - ✅ Text chunker with overlap
   - ✅ Embedder
   - ✅ Retriever
   - ✅ Complete RAG pipeline

5. **Function Calling Tools** (`/app/tools/`)
   - ✅ Base tool class
   - ✅ Banking tools (balance, transactions, payments)
   - ✅ Travel tools (flight search, etc.)
   - ✅ Research tools
   - ✅ Communication tools
   - ✅ Stock tools
   - ✅ Tool registry

6. **Database Layer** (`/app/database/`)
   - ✅ SQLAlchemy models (User, Permissions, Research, Travel, Banking, AuditLog, Documents)
   - ✅ Database manager
   - ✅ Async session handling

7. **API Endpoints** (`/app/routers/`)
   - ✅ `/chat` - Main conversation endpoint
   - ✅ `/memory` - Memory management
   - ✅ `/rag` - Document upload and query
   - ✅ `/tools` - Tool invocation
   - ✅ `/setup` - User and module setup

8. **Configuration & Security**
   - ✅ Environment-based config
   - ✅ CORS middleware
   - ✅ Pydantic validation
   - ✅ Structured logging

9. **Documentation**
   - ✅ Comprehensive README
   - ✅ API documentation (via FastAPI)
   - ✅ Sample curl requests
   - ✅ Environment template

10. **Testing**
    - ✅ Sample test suite
    - ✅ Test structure

---

## 🚀 Quick Start (Step-by-Step)

### Step 1: Install Dependencies

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2: Configure Environment

```powershell
copy .env.example .env
```

Edit `.env` and add your API keys:
```
OPENAI_API_KEY=sk-your-actual-key
ANTHROPIC_API_KEY=sk-ant-your-actual-key
GOOGLE_API_KEY=your-actual-key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
```

### Step 3: Setup Infrastructure (Optional)

**PostgreSQL:**
```powershell
# Install PostgreSQL or use Docker
docker run -d --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=anintelligentai -p 5432:5432 postgres:16
```

**Redis (Optional):**
```powershell
docker run -d --name redis -p 6379:6379 redis:7
```

**Qdrant (Optional):**
```powershell
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### Step 4: Run the Backend

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Test the API

Open browser:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or use curl:
```bash
curl http://localhost:8000/health
```

---

## 📋 First API Calls

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. List Available Tools
```bash
curl http://localhost:8000/api/v1/tools/list
```

### 3. Simple Chat (No Tools)
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","session_id":"sess1","message":"Hello!","use_tools":false}'
```

### 4. Chat with Banking Tool
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","session_id":"sess1","message":"What is my balance?","module":"banking","use_tools":true}'
```

---

## 🔧 Configuration Options

### Minimal Configuration (Testing)
Only OpenAI API key required:
```
OPENAI_API_KEY=sk-your-key
```

All other services have in-memory fallbacks:
- Redis → In-memory dict
- Qdrant → In-memory vector store
- Database → SQLite (change DATABASE_URL)

### Full Production Configuration
- PostgreSQL for persistence
- Redis for distributed caching
- Qdrant for vector search
- All 3 LLM providers configured

---

## 🛠️ Troubleshooting

### Issue: "Module not found"
```powershell
# Make sure you're in the backend directory and venv is activated
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "API key not configured"
```
# Edit .env file and add your API key
OPENAI_API_KEY=sk-your-actual-openai-key
```

### Issue: "Database connection error"
```
# Use SQLite for testing (change in .env):
DATABASE_URL=sqlite+aiosqlite:///./test.db

# Or start PostgreSQL:
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=pass postgres:16
```

### Issue: "Redis connection failed"
```
# Set REDIS_ENABLED=false in .env to use in-memory fallback
REDIS_ENABLED=false
```

---

## 📊 Project Structure

```
backend/
├── app/
│   ├── llm/              # LLM providers (OpenAI, Anthropic, Gemini)
│   ├── memory/           # Hybrid memory system
│   ├── prompts/          # System and module prompts
│   ├── rag/              # Document processing and retrieval
│   ├── tools/            # Function calling tools
│   ├── database/         # SQLAlchemy models
│   ├── routers/          # FastAPI endpoints
│   ├── services/         # Business logic
│   ├── config.py         # Configuration management
│   ├── schemas.py        # Pydantic models
│   └── main.py           # FastAPI application
├── tests/                # Unit and integration tests
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md             # Full documentation
```

---

## 🎯 Next Steps

1. **Add Your API Keys**: Edit `.env` with real keys
2. **Test Endpoints**: Use the interactive docs at `/docs`
3. **Explore Tools**: Try different function calls
4. **Upload Documents**: Test the RAG pipeline
5. **Customize Prompts**: Edit prompts in `/app/prompts/`
6. **Add New Tools**: Extend `/app/tools/` with custom tools

---

## 📚 Key Files to Review

- `app/main.py` - Application entry point
- `app/config.py` - All configuration settings
- `app/services/chat_service.py` - Core chat logic
- `app/tools/tool_registry.py` - Tool management
- `app/memory/memory_orchestrator.py` - Memory coordination

---

## 🔐 Security Notes

**IMPORTANT for Production:**
1. Change `SECRET_KEY` and `ENCRYPTION_KEY` in `.env`
2. Use strong database passwords
3. Enable HTTPS
4. Set proper CORS origins
5. Configure rate limiting
6. Enable audit logging
7. Regular security audits

---

## ✅ Verification Checklist

- [ ] Dependencies installed
- [ ] `.env` file configured with API key
- [ ] Server starts without errors
- [ ] Health endpoint returns 200
- [ ] Can list tools via API
- [ ] Basic chat works
- [ ] Tool invocation works
- [ ] OpenAPI docs accessible at `/docs`

---

## 📞 Getting Help

- Check `/docs` endpoint for interactive API documentation
- See `README.md` for comprehensive documentation
- Check logs for detailed error messages

---

**🎉 Your AnIntelligentAI backend is ready!**

Start building your AI-powered applications with this production-grade foundation.
