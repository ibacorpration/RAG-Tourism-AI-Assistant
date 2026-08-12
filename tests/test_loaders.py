from pathlib import Path
import pytest
from app.services.loaders.text import TextLoader
from app.services.loaders.factory import LoaderFactory
from app.services.splitters.text_splitter import TextSplitter
from app.services.documents.document import Document


def test_text_loader(tmp_path):
    test_file = tmp_path / "sample.txt"
    test_file.write_text("Hello, RAG System! This is a test document.", encoding="utf-8")

    loader = TextLoader()
    doc = loader.load(test_file)

    assert isinstance(doc, Document)
    assert doc.content == "Hello, RAG System! This is a test document."
    assert doc.metadata["source"] == "sample.txt"


def test_loader_factory(tmp_path):
    txt_file = tmp_path / "doc.txt"
    txt_file.write_text("Content", encoding="utf-8")

    loader = LoaderFactory.get_loader(txt_file)
    assert isinstance(loader, TextLoader)


def test_text_splitter():
    doc = Document(
        content="First paragraph text.\n\nSecond paragraph text is longer and contains more details about the RAG system."
    )
    splitter = TextSplitter(chunk_size=50, chunk_overlap=10)
    chunks = splitter.split_document(doc)

    assert len(chunks) > 0
    assert all(chunk.doc_id == doc.id for chunk in chunks)
