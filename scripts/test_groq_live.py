import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.llms.groq_llm import GroqLLMProvider
from app.core.config import settings

def main():
    print(f"Testing Groq API with Model: {settings.GROQ_MODEL_NAME}")
    provider = GroqLLMProvider()
    response = provider.generate("Explain RAG systems in one sentence.")
    print("\n--- Groq API Live Response ---")
    print(response)
    print("------------------------------")

if __name__ == "__main__":
    main()
