import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.schemas.upload import DocumentUploadResponse, DocumentDeleteResponse, SyncResponse
from app.services.rag.rag_service import RAGService
from app.api.dependencies import get_rag_service
from app.core.config import settings
from app.core.constants import SUPPORTED_EXTENSIONS
from app.core.exceptions import RAGException
from app.core.logger import logger

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, tags=["Document Ingestion"])
async def upload_document(
    file: UploadFile = File(...),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Uploads a document (PDF, TXT, MD, JSON), saves it to storage, and indexes its vector embeddings.
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_ext}'. Supported extensions are: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    upload_dir = settings.BASE_DIR / settings.UPLOADS_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination_path = upload_dir / file.filename

    try:
        with destination_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Saved uploaded file to: {destination_path}")

        # Ingest & Index document
        result = rag_service.ingest_file(destination_path)

        return DocumentUploadResponse(
            filename=result["filename"],
            file_type=result["file_type"],
            file_size_bytes=result["file_size_bytes"],
            chunks_created=result["chunks_created"],
            vectors_indexed=result["vectors_indexed"],
            message=result["message"],
            metadata={"saved_path": str(destination_path)}
        )
    except RAGException as e:
        logger.error(f"RAG error processing upload for {file.filename}: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error handling file upload: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"File upload failed: {str(e)}")


@router.delete("/upload/{filename}", response_model=DocumentDeleteResponse, tags=["Document Ingestion"])
async def delete_document(
    filename: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Deletes a document: removes its file from the uploads folder AND purges
    all of its chunks/vectors from the vector store. This is the recommended
    way to remove a document (it's instant, unlike a manual filesystem
    delete which relies on the background sync to catch up).
    """
    try:
        result = rag_service.delete_document(filename)
        if result["vectors_removed"] == 0 and not result["file_removed"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No document named '{filename}' found on disk or in the vector store."
            )
        return DocumentDeleteResponse(**result)
    except HTTPException:
        raise
    except RAGException as e:
        logger.error(f"RAG error deleting document '{filename}': {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error deleting document '{filename}': {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Delete failed: {str(e)}")


@router.post("/upload/sync", response_model=SyncResponse, tags=["Document Ingestion"])
async def sync_uploads(
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Manually reconciles the vector store with the uploads folder: any
    indexed document whose file is no longer on disk gets purged. Useful
    right after deleting files directly from the data folder, in addition
    to the automatic background watcher.
    """
    try:
        result = rag_service.sync_with_uploads_dir()
        return SyncResponse(**result)
    except RAGException as e:
        logger.error(f"RAG error during sync: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error during sync: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Sync failed: {str(e)}")
