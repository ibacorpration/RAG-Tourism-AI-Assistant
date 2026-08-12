from functools import lru_cache
from app.services.embeddings.sentence_transformer import SentenceTransformerEmbedding
from app.services.vector_store.chroma import ChromaVectorStore
from app.services.rag.rag_service import RAGService
from app.services.rag.chat_service import RAGChatService
from app.services.llms.groq_llm import GroqLLMProvider
from app.services.memory.in_memory import InMemoryConversationMemory


@lru_cache()
def get_embedding_provider() -> SentenceTransformerEmbedding:
    return SentenceTransformerEmbedding()


@lru_cache()
def get_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore()


@lru_cache()
def get_memory() -> InMemoryConversationMemory:
    return InMemoryConversationMemory()


@lru_cache()
def get_llm_provider() -> GroqLLMProvider:
    return GroqLLMProvider()


def get_rag_service() -> RAGService:
    embedding_provider = get_embedding_provider()
    vector_store = get_vector_store()
    return RAGService(embedding_provider=embedding_provider, vector_store=vector_store)


def get_rag_chat_service() -> RAGChatService:
    rag_service = get_rag_service()
    memory = get_memory()
    llm_provider = get_llm_provider()
    return RAGChatService(rag_service=rag_service, llm_provider=llm_provider, memory=memory)
