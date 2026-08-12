from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.embeddings import VectorSearchRequest, VectorSearchResponse, SearchResultChunk, CollectionStatsResponse
from app.services.rag.rag_service import RAGService
from app.services.vector_store.base import BaseVectorStore
from app.api.dependencies import get_rag_service, get_vector_store
from app.core.exceptions import RAGException
from app.core.logger import logger

router = APIRouter()


@router.post("/embeddings/search", response_model=VectorSearchResponse, tags=["Vector Store & Retrieval"])
async def search_vectors(
    request: VectorSearchRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Executes a vector similarity or MMR retrieval search against the indexed document collection.
    """
    try:
        raw_results = rag_service.search(
            query=request.query,
            top_k=request.top_k,
            use_mmr=request.use_mmr,
            score_threshold=request.score_threshold
        )

        chunks = [
            SearchResultChunk(
                chunk_id=res["chunk_id"],
                content=res["content"],
                similarity_score=res["similarity_score"],
                metadata=res["metadata"]
            )
            for res in raw_results
        ]

        return VectorSearchResponse(
            query=request.query,
            retrieved_count=len(chunks),
            results=chunks
        )
    except RAGException as e:
        logger.error(f"Vector search failed: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in vector search: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/embeddings/stats", response_model=CollectionStatsResponse, tags=["Vector Store & Retrieval"])
async def get_collection_stats(
    vector_store: BaseVectorStore = Depends(get_vector_store)
):
    """
    Returns total vector count and stats of the active ChromaDB collection.
    """
    try:
        stats = vector_store.get_stats()
        return CollectionStatsResponse(
            collection_name=stats["collection_name"],
            total_vectors=stats["total_vectors"],
            total_documents=stats["total_documents"],
            embedding_model=stats["embedding_model"]
        )
    except Exception as e:
        logger.error(f"Failed to fetch vector stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
