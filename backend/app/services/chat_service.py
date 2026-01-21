"""Chat Service - Core chat processing logic with RAG integration."""

import logging
from typing import Dict, Any, List, Optional
from app.schemas import ChatRequest, ChatResponse
from app.llm.provider_factory import ProviderFactory, ProviderType
from app.prompts import get_prompt_for_module, BASE_SYSTEM_PROMPT
from app.tools.tool_registry import ToolRegistry
from app.services.knowledge_base_loader import knowledge_loader
from app.rag.rag_pipeline import RAGPipeline
from app.memory.vector_memory import VectorMemory
from app.config import settings

logger = logging.getLogger(__name__)


class ChatService:
    """Service for processing chat messages with RAG and knowledge base integration."""

    def __init__(self):
        """Initialize chat service."""
        self.provider_factory = ProviderFactory
        ToolRegistry.initialize()
        self._rag_pipeline: Optional[RAGPipeline] = None
        self._vector_memory: Optional[VectorMemory] = None
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message with full RAG and knowledge base integration.

        Args:
            request: ChatRequest with user message and options

        Returns:
            ChatResponse with AI reply
        """
        logger.info(f"Processing message for user {request.user_id}: {request.message[:100]}...")

        try:
            # Get LLM provider
            provider = self._get_provider()

            # 1. Build base system prompt
            base_prompt = get_prompt_for_module(request.module) if request.module else BASE_SYSTEM_PROMPT

            # 2. Enhance with knowledge base context
            knowledge_context = ""
            knowledge_snippet = ""
            if request.message:
                enhanced_prompt, knowledge_snippet = knowledge_loader.enhance_prompt_with_knowledge(
                    request.message,
                    base_prompt
                )
                base_prompt = enhanced_prompt
                knowledge_context = knowledge_snippet[:500] if knowledge_snippet else ""
                logger.info(f"Knowledge base enhanced prompt with: {knowledge_context[:100]}...")

            # 3. Get RAG context if enabled
            rag_context = ""
            rag_sources = []
            if request.use_rag:
                try:
                    rag_result = await self._get_rag_context(
                        user_id=request.user_id,
                        query=request.message,
                        provider=provider
                    )
                    if rag_result:
                        rag_context = rag_result.get('context', '')
                        rag_sources = rag_result.get('sources', [])
                        logger.info(f"RAG found {len(rag_sources)} relevant sources")
                except Exception as e:
                    logger.warning(f"RAG context retrieval failed: {e}")

            # 4. Build final system prompt with all context
            final_system_prompt = base_prompt
            if rag_context:
                final_system_prompt += f"\n\n**CONTEXT FROM USER'S DOCUMENTS:**\n{rag_context}"

            # 5. Build messages
            messages = [
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": request.message}
            ]

            # 6. Get tools if enabled
            tools = None
            if request.use_tools:
                tools = ToolRegistry.get_all_schemas()
                logger.info(f"Enabled {len(tools)} tools for this request")

            # 7. Generate response with better parameters
            llm_response = await provider.chat_completion(
                messages=messages,
                temperature=0.7,  # Balanced creativity
                max_tokens=2000,  # Allow longer responses
                functions=tools
            )

            # 8. Check for tool calls and handle them properly
            tool_calls = []
            final_response = llm_response.content

            if llm_response.function_call:
                tool_name = llm_response.function_call.get('name')
                logger.info(f"Tool called: {tool_name}")

                # Execute tool
                tool_result = await self._execute_tool_call(
                    request.user_id,
                    llm_response.function_call
                )
                tool_calls.append(tool_result)

                # If tool was successful, generate a follow-up response with the result
                if tool_result.get('success'):
                    follow_up_messages = messages + [
                        {"role": "assistant", "content": llm_response.content or "Let me get that information for you."},
                        {"role": "function", "name": tool_name,
                         "content": str(tool_result.get('data', {}))}
                    ]

                    follow_up_response = await provider.chat_completion(
                        messages=follow_up_messages,
                        temperature=0.7,
                        max_tokens=1500
                    )
                    final_response = follow_up_response.content
                else:
                    # Tool failed - provide helpful response without tool data
                    error_msg = tool_result.get('message', 'The requested operation is not available')
                    logger.warning(f"Tool {tool_name} failed: {error_msg}")

                    # Generate response explaining the limitation and providing alternative info
                    fallback_messages = messages + [
                        {"role": "assistant", "content": f"I attempted to use {tool_name} but it's currently not available. Let me provide you with information based on my knowledge instead."},
                    ]

                    fallback_response = await provider.chat_completion(
                        messages=fallback_messages,
                        temperature=0.7,
                        max_tokens=1500
                    )
                    final_response = fallback_response.content

            # 9. Combine all sources
            all_sources = []
            if knowledge_context:
                all_sources.append({
                    "type": "knowledge_base",
                    "content": knowledge_snippet[:200],
                    "relevance": "high"
                })
            all_sources.extend(rag_sources)

            logger.info(f"Chat completed: {llm_response.tokens_used} tokens, {len(tool_calls)} tool calls")

            return ChatResponse(
                response=final_response,
                tokens_used=llm_response.tokens_used,
                tool_calls=tool_calls,
                sources=all_sources,
                session_id=request.session_id
            )

        except Exception as e:
            logger.error(f"Chat processing error: {e}", exc_info=True)
            return ChatResponse(
                response=f"I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
                tokens_used=0,
                tool_calls=[],
                sources=[],
                session_id=request.session_id
            )
    
    def _get_provider(self):
        """Get LLM provider based on settings."""
        provider_type = ProviderType(settings.DEFAULT_LLM_PROVIDER)
        
        if provider_type == ProviderType.OPENAI:
            api_key = settings.OPENAI_API_KEY
        elif provider_type == ProviderType.ANTHROPIC:
            api_key = settings.ANTHROPIC_API_KEY
        elif provider_type == ProviderType.GEMINI:
            api_key = settings.GOOGLE_API_KEY
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
        
        if not api_key:
            raise ValueError(f"API key not configured for {provider_type}")
        
        return self.provider_factory.create_provider(
            provider_type=provider_type,
            api_key=api_key,
            model=settings.DEFAULT_CHAT_MODEL
        )
    
    async def _get_rag_context(
        self,
        user_id: str,
        query: str,
        provider: Any,
        top_k: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Get RAG context from user's uploaded documents.

        Args:
            user_id: User identifier
            query: User query
            provider: LLM provider for embeddings
            top_k: Number of chunks to retrieve

        Returns:
            RAG context with sources
        """
        try:
            # Initialize RAG pipeline if needed
            if not self._rag_pipeline:
                if not self._vector_memory:
                    try:
                        self._vector_memory = VectorMemory(qdrant_url=settings.QDRANT_URL)
                    except Exception as e:
                        logger.warning(f"Vector memory initialization failed: {e}")
                        return None

                self._rag_pipeline = RAGPipeline(
                    llm_provider=provider,
                    vector_memory=self._vector_memory
                )

            # Query the RAG pipeline
            result = await self._rag_pipeline.query(
                user_id=user_id,
                query=query,
                top_k=top_k,
                score_threshold=0.7
            )

            if result and result.get('chunks'):
                return {
                    'context': result.get('context', ''),
                    'sources': [
                        {
                            'type': 'document',
                            'filename': chunk['metadata'].get('filename', 'Unknown'),
                            'relevance': chunk.get('score', 0),
                            'excerpt': chunk['text'][:200]
                        }
                        for chunk in result['chunks']
                    ]
                }

            return None

        except Exception as e:
            logger.error(f"RAG context retrieval error: {e}")
            return None
    
    async def _execute_tool_call(self, user_id: str, function_call: Dict[str, Any]) -> Dict:
        """Execute a tool call."""
        import json
        
        tool_name = function_call["name"]
        
        # Parse arguments (may be string or dict)
        if isinstance(function_call["arguments"], str):
            arguments = json.loads(function_call["arguments"])
        else:
            arguments = function_call["arguments"]
        
        # Execute tool with default permissions
        # For now, grant all permissions. In production, get from user's role/profile
        default_permissions = {
            "banking_read": True,
            "banking_write": True,
            "travel_read": True,
            "travel_write": True,
            "research_read": True,
            "stocks_read": True,
            "communication_read": True,
            "communication_write": True,
        }

        result = await ToolRegistry.execute_tool(
            tool_name=tool_name,
            user_id=user_id,
            parameters=arguments,
            permissions=default_permissions
        )
        
        return {
            "tool": tool_name,
            "success": result.success,
            "data": result.data,
            "message": result.message
        }
