
# AI Assistant Demo (Mock LLM)

This is a minimal demo project for the **AI Personal Assistant** focusing on the AI backend.
It uses a **mock LLM provider** so you can run it locally without API keys and demo core flows:
- LLM adapter (provider-agnostic)
- Session memory
- Persona/system prompt injection
- Module-aware responses (banking, travel, research, communication, stock) via mock rules

## Quick start (VS Code)

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .\.venv\Scripts\activate  # Windows (PowerShell)
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. Example curl:
   ```bash
   curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{
     "user_id":"user_123",
     "modules":["banking"],
     "message":"What is my checking account balance?",
     "ai_name":"Ava",
     "tone":"Friendly"
   }'
   ```

5. Expected result: JSON with `response` field containing a friendly mock reply.

## Files
- `main.py` - FastAPI app
- `llm_adapter.py` - Adapter + MockProvider
- `prompts.py` - System prompt template
- `memory.py` - In-memory session memory
- `schemas.py` - Pydantic request/response models
- `requirements.txt` - Python deps

## Next steps (for production)
- Replace `MockProvider` with a real LLM provider in `llm_adapter.py`.
- Add vector DB and RAG pipeline.
- Add secure vault for credentials.
- Implement function-calling/structured action handlers on server-side.

