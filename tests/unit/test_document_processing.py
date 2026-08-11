"""Unit checks for bounded parsing, scanning, storage, and embeddings."""

from pathlib import Path

import pytest

from careerpilot_api.document_processing import (
    BoundedDocumentParser,
    DeterministicHashEmbedder,
    LocalDocumentScanner,
    LocalFilesystemDocumentStorage,
)


def test_text_processing_is_bounded_and_deterministic(tmp_path: Path) -> None:
    parser = BoundedDocumentParser()
    sections = parser.parse("text/plain", b"Python\r\n  PostgreSQL\x01 skills")
    assert sections[0].text == "Python\nPostgreSQL skills"
    embedder = DeterministicHashEmbedder()
    assert embedder.embed("Python PostgreSQL") == embedder.embed("python postgresql")
    assert len(embedder.embed("Python")) == 64

    storage = LocalFilesystemDocumentStorage(tmp_path)
    key = storage.put("tenant-a", "document-a", b"private synthetic bytes")
    assert storage.read(key) == b"private synthetic bytes"
    storage.delete(key)
    with pytest.raises(FileNotFoundError):
        storage.read(key)


def test_scanner_and_parser_fail_closed() -> None:
    scanner = LocalDocumentScanner()
    assert not scanner.scan("bad.pdf", "application/pdf", b"not-pdf").clean
    assert not scanner.scan(
        "bad.txt", "text/plain", b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE"
    ).clean
    with pytest.raises(ValueError, match="invalid_utf8"):
        BoundedDocumentParser().parse("text/plain", b"\xff")
