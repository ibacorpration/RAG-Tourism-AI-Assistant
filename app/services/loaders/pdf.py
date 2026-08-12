from pathlib import Path
from pypdf import PdfReader
from app.services.loaders.base import BaseLoader
from app.services.documents.document import Document
from app.core.exceptions import DocumentProcessingError
from app.core.logger import logger


class PDFLoader(BaseLoader):
    """
    Loader for PDF (.pdf) documents using PyPDF.
    """

    def load(self, file_path: Path) -> Document:
        file_path = Path(file_path)
        if not file_path.exists():
            raise DocumentProcessingError(f"PDF file not found: {file_path}")

        try:
            reader = PdfReader(str(file_path))
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(text)

            full_text = "\n\n".join(pages_text)
            metadata = {
                "source": file_path.name,
                "file_path": str(file_path),
                "file_type": ".pdf",
                "file_size": file_path.stat().st_size,
                "num_pages": len(reader.pages)
            }
            logger.info(f"Successfully loaded PDF document: {file_path.name} ({len(reader.pages)} pages)")
            return Document(content=full_text, metadata=metadata)
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {e}")
            raise DocumentProcessingError(f"Failed to process PDF document: {e}")
