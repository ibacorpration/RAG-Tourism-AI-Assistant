from pathlib import Path
from app.services.loaders.base import BaseLoader
from app.services.documents.document import Document
from app.core.exceptions import DocumentProcessingError
from app.core.logger import logger


class TextLoader(BaseLoader):
    """
    Loader for Plain Text (.txt), Markdown (.md), and JSON files.
    """

    def load(self, file_path: Path) -> Document:
        file_path = Path(file_path)
        if not file_path.exists():
            raise DocumentProcessingError(f"File not found: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            metadata = {
                "source": file_path.name,
                "file_path": str(file_path),
                "file_type": file_path.suffix.lower(),
                "file_size": file_path.stat().st_size
            }
            logger.info(f"Successfully loaded text document: {file_path.name}")
            return Document(content=content, metadata=metadata)
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {e}")
            raise DocumentProcessingError(f"Failed to load text file: {e}")
