from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.embeddings import SearchResultChunk
from app.services.rag.chat_service import RAGChatService
from app.services.memory.base import BaseMemory
from app.api.dependencies import get_rag_chat_service, get_memory
from app.core.exceptions import LLMRateLimitError, RAGException
from app.core.logger import logger

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["RAG Chatbot"])
async def chat_completion(
    request: ChatRequest,
    chat_service: RAGChatService = Depends(get_rag_chat_service)
):
    """
    Synchronous RAG Chat completion endpoint with context grounding and source attribution.
    """
    try:
        result = chat_service.chat(
            user_message=request.message,
            conversation_id=request.conversation_id
        )

        sources = [
            SearchResultChunk(
                chunk_id=src["chunk_id"],
                content=src["content"],
                similarity_score=src["similarity_score"],
                metadata=src["metadata"]
            )
            for src in result["sources"]
        ]

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            sources=sources
        )
    except LLMRateLimitError as e:
        logger.error(f"Rate limit in chat completion: {e.message}")
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=e.message)
    except RAGException as e:
        logger.error(f"RAG error in chat completion: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/chat/stream", tags=["RAG Chatbot"])
async def chat_stream(
    request: ChatRequest,
    chat_service: RAGChatService = Depends(get_rag_chat_service)
):
    """
    Streaming RAG Chat endpoint transmitting generated tokens in real time (Server-Sent Events).
    """
    try:
        token_generator = chat_service.chat_stream(
            user_message=request.message,
            conversation_id=request.conversation_id
        )

        def event_stream():
            try:
                for token in token_generator:
                    yield f"data: {token}\n\n"
            except LLMRateLimitError as e:
                yield f"data: [ERROR] {e.message}\n\n"
            except RAGException as e:
                yield f"data: [ERROR] {e.message}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error in streaming chat: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/chat/history/{conversation_id}", tags=["RAG Chatbot"])
async def clear_chat_history(
    conversation_id: str,
    memory: BaseMemory = Depends(get_memory)
):
    """
    Clears the conversation memory history for a given conversation ID.
    """
    memory.clear_history(conversation_id)
    return {"message": f"Cleared history for conversation '{conversation_id}'."}
