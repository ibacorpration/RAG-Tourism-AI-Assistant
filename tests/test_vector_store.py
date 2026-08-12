import pytest
from app.services.documents.document import DocumentChunk
from app.services.vector_store.chroma import ChromaVectorStore


def test_chroma_vector_store(tmp_path):
    store = ChromaVectorStore(persist_dir=str(tmp_path / "test_chroma"), collection_name="test_collection")

    chunk1 = DocumentChunk(doc_id="doc1", content="RAG retrieves relevant context.", chunk_index=0)
    chunk2 = DocumentChunk(doc_id="doc1", content="LLM generates output based on context.", chunk_index=1)

    # Mock embeddings (vector dimension = 4 for testing)
    embeddings = [
        [0.1, 0.2, 0.3, 0.4],
        [0.4, 0.3, 0.2, 0.1]
    ]

    added_count = store.add_chunks([chunk1, chunk2], embeddings)
    assert added_count == 2

    stats = store.get_stats()
    assert stats["total_vectors"] == 2

    search_res = store.similarity_search(query_embedding=[0.1, 0.2, 0.3, 0.4], top_k=1)
    assert len(search_res) == 1
    assert search_res[0]["content"] == "RAG retrieves relevant context."
