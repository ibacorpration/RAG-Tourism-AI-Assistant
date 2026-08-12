from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_rag_chat_service

client = TestClient(app)


def mock_chat_service():
    service = MagicMock()
    service.chat.return_value = {
        "conversation_id": "test-chat-session",
        "response": "This is a RAG answer powered by Groq API.",
        "sources": [
            {
                "chunk_id": "chunk-1",
                "content": "RAG overview content",
                "similarity_score": 0.95,
                "metadata": {"source": "rag_overview.txt"}
            }
        ]
    }
    
    def mock_stream(*args, **kwargs):
        yield "This "
        yield "is "
        yield "streamed."

    service.chat_stream.side_effect = mock_stream
    return service


# Override dependency for API tests
app.dependency_overrides[get_rag_chat_service] = mock_chat_service


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "RAG-Chatbot"


def test_chat_completion_endpoint():
    response = client.post(
        "/api/v1/chat",
        json={"message": "What is RAG?", "conversation_id": "test-chat-session"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["conversation_id"] == "test-chat-session"


def test_chat_streaming_endpoint():
    response = client.post(
        "/api/v1/chat/stream",
        json={"message": "Explain vector indexing", "conversation_id": "test-stream-session"}
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


def test_clear_chat_history_endpoint():
    response = client.delete("/api/v1/chat/history/test-chat-session")
    assert response.status_code == 200
    data = response.json()
    assert "Cleared history" in data["message"]
