# Frontend-Backend Integration Guide

This guide explains how to connect and run the frontend and backend together.

## Prerequisites

### Backend Requirements
- Python 3.10+
- PostgreSQL database
- Redis server
- Qdrant vector database (optional)
- OpenAI API key (or Anthropic/Google AI)

### Frontend Requirements
- Node.js 18+
- npm or yarn

## Quick Start

### 1. Start the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env file with your credentials

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 2. Start the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at: `http://localhost:3000`

## Environment Configuration

### Backend (.env)

```env
# Required settings
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/anintelligentai

# LLM API Key (at least one required)
OPENAI_API_KEY=sk-your-openai-key

# Optional services
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
```

### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |
| PUT | `/api/v1/auth/me` | Update profile |
| POST | `/api/v1/auth/change-password` | Change password |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/` | Send chat message |
| GET | `/api/v1/chat/history/{session_id}` | Get chat history |
| GET | `/api/v1/chat/sessions` | List user sessions |
| DELETE | `/api/v1/chat/sessions/{session_id}` | Delete session |

### Tools
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tools/list` | List available tools |
| POST | `/api/v1/tools/invoke` | Invoke a tool |
| GET | `/api/v1/tools/{tool_name}` | Get tool details |

### Documents (RAG)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rag/upload` | Upload document |
| POST | `/api/v1/rag/query` | Query documents |
| GET | `/api/v1/rag/documents` | List documents |
| DELETE | `/api/v1/rag/documents/{id}` | Delete document |

### Memory
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/memory/add` | Add memory fact |
| POST | `/api/v1/memory/get` | Get memory facts |
| GET | `/api/v1/memory/conversation/{session_id}` | Get conversation |
| GET | `/api/v1/memory/summaries` | Get summaries |

### Setup
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/setup/modules` | List modules |
| POST | `/api/v1/setup/modules` | Update modules |
| GET | `/api/v1/setup/profile` | Get profile |
| POST | `/api/v1/setup/profile` | Update profile |

## Authentication Flow

1. **Registration**: POST to `/auth/register` with email, password, full_name
2. **Login**: POST to `/auth/login` with email, password
   - Returns: `access_token`, `refresh_token`
3. **Get User**: GET `/auth/me` with Authorization header
4. **Refresh Token**: POST to `/auth/refresh` with refresh_token

### Token Usage
```javascript
// Authorization header format
headers: {
  'Authorization': 'Bearer <access_token>'
}
```

## Demo Mode

The frontend includes a Demo Mode for testing without a backend:
1. Click "Try Demo Mode" on the login page
2. Explore the interface with mock data
3. Full functionality requires backend connection

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:8080` (alternative port)
- `http://localhost:5173` (Vite dev server)
- `https://frontend-rho-six-34.vercel.app` (Vercel deployment)
- `https://*.vercel.app` (All Vercel deployments)

## Deployment

### Backend (Recommended: Railway, Render, or AWS)

1. Set environment variables in deployment platform
2. Use production PostgreSQL database
3. Configure Redis and Qdrant services
4. Set proper SECRET_KEY

### Frontend (Recommended: Vercel)

1. Connect GitHub repository
2. Set environment variable:
   ```
   REACT_APP_API_URL=https://your-backend-url.com/api/v1
   ```
3. Deploy automatically

## Troubleshooting

### CORS Errors
- Ensure backend CORS_ORIGINS includes frontend URL
- Check that credentials are being sent properly

### Authentication Errors
- Verify tokens are being stored correctly
- Check token expiration (default: 60 minutes)
- Ensure refresh token flow is working

### API Connection Issues
- Verify backend is running on correct port
- Check REACT_APP_API_URL in frontend .env
- Test API directly at `/docs` endpoint

## Development Tips

1. **Backend logs**: Watch terminal for request/response logs
2. **Frontend console**: Check browser DevTools for API errors
3. **Network tab**: Inspect actual HTTP requests/responses
4. **API docs**: Use Swagger UI at `/docs` for testing endpoints
