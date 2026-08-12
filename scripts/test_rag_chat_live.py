import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.dependencies import get_rag_chat_service

def main():
    chat_service = get_rag_chat_service()
    query = "What is Retrieval-Augmented Generation according to the indexed documents?"
    print(f"Sending RAG Query: '{query}'")
    result = chat_service.chat(user_message=query)
    
    print("\n================ RAG RESPONSE ================")
    print(result["response"])
    print("==============================================")
    print("\nSources Retrieved:")
    for src in result["sources"]:
        print(f" - {src['metadata'].get('source')} (Score: {src['similarity_score']})")

if __name__ == "__main__":
    main()
