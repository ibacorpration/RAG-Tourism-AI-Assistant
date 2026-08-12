import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.dependencies import get_rag_service
from app.core.logger import logger
from app.core.constants import SUPPORTED_EXTENSIONS


def main():
    parser = argparse.ArgumentParser(description="RAG Document Ingestion CLI Tool")
    parser.add_argument("--path", type=str, required=True, help="File or directory path to ingest into RAG Vector Store")
    args = parser.parse_args()

    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"Error: Target path '{target_path}' does not exist.")
        sys.exit(1)

    rag_service = get_rag_service()

    # Reconcile first: any document previously indexed whose file is no
    # longer inside this folder gets fully removed from the vector store.
    # This is what makes re-running the script reflect ONLY what's
    # currently in the data folder (deleted files stop being answered from).
    sync_result = rag_service.sync_with_uploads_dir(target_path if target_path.is_dir() else target_path.parent)
    if sync_result["removed"]:
        print(f"Removed {len(sync_result['removed'])} document(s) no longer present in the folder:")
        for item in sync_result["removed"]:
            print(f"  - {item['filename']} ({item['vectors_removed']} vectors purged)")

    files_to_process = []
    if target_path.is_file():
        if target_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files_to_process.append(target_path)
        else:
            print(f"Error: Unsupported file format '{target_path.suffix}'. Supported formats: {SUPPORTED_EXTENSIONS}")
            sys.exit(1)
    else:
        for ext in SUPPORTED_EXTENSIONS:
            files_to_process.extend(target_path.rglob(f"*{ext}"))

    if not files_to_process:
        print(f"No processable documents found at '{target_path}'.")
        sys.exit(0)

    print(f"Found {len(files_to_process)} document(s) to process.")
    for file_path in files_to_process:
        print(f"Processing: {file_path.name} ...")
        try:
            result = rag_service.ingest_file(file_path)
            print(f"  -> Success! Indexed {result['vectors_indexed']} vectors ({result['chunks_created']} chunks).")
        except Exception as e:
            print(f"  -> Failed! Error: {e}")

    print("\nIngestion process completed.")


if __name__ == "__main__":
    main()
