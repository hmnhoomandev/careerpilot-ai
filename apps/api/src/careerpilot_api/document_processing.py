"""Local secure-document adapters for storage, scanning, parsing, and embeddings."""

from __future__ import annotations

import hashlib
import math
import os
import re
import tempfile
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from careerpilot_core import ParsedSection, ScanResult

EMBEDDING_DIMENSIONS = 64
MAX_PDF_PAGES = 50
MAX_PDF_PAGE_CONTENT_BYTES = 2 * 1024 * 1024
MAX_EXTRACTED_CHARACTERS = 500_000
MAX_TEXT_CHARACTERS = 500_000
TOKEN_PATTERN = re.compile(r"[a-z][a-z0-9+#.-]{1,}")
EICAR_MARKER = b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE"
ACTIVE_PDF_MARKERS = (b"/JavaScript", b"/JS", b"/Launch", b"/EmbeddedFile")
FIRST_PRINTABLE_CODEPOINT = 32


class LocalDocumentScanner:
    """Fail closed on known test malware and declared-type/magic mismatch."""

    def scan(self, filename: str, media_type: str, content: bytes) -> ScanResult:
        """Apply deterministic local checks without executing uploaded content."""
        del filename
        if EICAR_MARKER in content:
            return ScanResult(clean=False, reason="malware_signature_detected")
        if media_type == "application/pdf" and not content.startswith(b"%PDF-"):
            return ScanResult(clean=False, reason="content_type_mismatch")
        if media_type == "application/pdf" and any(
            marker in content for marker in ACTIVE_PDF_MARKERS
        ):
            return ScanResult(clean=False, reason="active_pdf_content_rejected")
        if media_type == "text/plain" and b"\x00" in content:
            return ScanResult(clean=False, reason="binary_text_rejected")
        return ScanResult(clean=True, reason="local_policy_clean")


class BoundedDocumentParser:
    """Extract UTF-8 or PDF text under explicit page/content/output limits."""

    def parse(self, media_type: str, content: bytes) -> tuple[ParsedSection, ...]:
        """Return normalized per-page sections; OCR and active content are excluded."""
        if media_type == "text/plain":
            return self._parse_text(content)
        if media_type == "application/pdf":
            return self._parse_pdf(content)
        raise ValueError("unsupported_media_type")

    @staticmethod
    def _parse_text(content: bytes) -> tuple[ParsedSection, ...]:
        try:  # parsing library failures are converted at this trust boundary
            text = content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("invalid_utf8") from error
        if len(text) > MAX_TEXT_CHARACTERS:
            raise ValueError("extracted_text_too_large")
        return (ParsedSection(page_number=1, text=_normalize_text(text)),)

    @staticmethod
    def _parse_pdf(content: bytes) -> tuple[ParsedSection, ...]:
        try:
            reader = PdfReader(BytesIO(content), strict=True)
            if reader.is_encrypted:
                raise ValueError("encrypted_pdf_not_supported")  # noqa: TRY301
            if len(reader.pages) > MAX_PDF_PAGES:
                raise ValueError("too_many_pages")  # noqa: TRY301
            sections: list[ParsedSection] = []
            extracted_characters = 0
            for page_number, page in enumerate(reader.pages, start=1):
                page_content = page.get_contents()
                if (
                    page_content is not None
                    and len(page_content.get_data()) > MAX_PDF_PAGE_CONTENT_BYTES
                ):
                    raise ValueError("pdf_content_stream_too_large")  # noqa: TRY301
                text = _normalize_text(page.extract_text() or "")
                extracted_characters += len(text)
                if extracted_characters > MAX_EXTRACTED_CHARACTERS:
                    raise ValueError("extracted_text_too_large")  # noqa: TRY301
                sections.append(ParsedSection(page_number=page_number, text=text))
        except ValueError:
            raise
        except Exception as error:
            raise ValueError("invalid_pdf") from error
        return tuple(sections)


class DeterministicHashEmbedder:
    """Free reproducible baseline embedding; not a neural semantic model."""

    @property
    def version(self) -> str:
        """Identify vectors that may be compared in one index."""
        return "deterministic-hash-64-v1"

    def embed(self, text: str) -> tuple[float, ...]:
        """Hash normalized terms into a signed unit-length bag-of-terms vector."""
        vector = [0.0] * EMBEDDING_DIMENSIONS
        for token in TOKEN_PATTERN.findall(text.casefold()):
            digest = hashlib.sha256(token.encode()).digest()
            index = int.from_bytes(digest[:2]) % EMBEDDING_DIMENSIONS
            sign = 1.0 if digest[2] & 1 else -1.0
            vector[index] += sign
        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude:
            vector = [value / magnitude for value in vector]
        return tuple(vector)


class InMemoryDocumentStorage:
    """Process-local byte store for default offline tests."""

    def __init__(self) -> None:
        self._content: dict[str, bytes] = {}

    def put(self, tenant_id: str, document_id: str, content: bytes) -> str:
        key = f"{tenant_id}/{document_id}"
        self._content[key] = bytes(content)
        return key

    def read(self, storage_key: str) -> bytes:
        return self._content[storage_key]

    def delete(self, storage_key: str) -> None:
        self._content.pop(storage_key, None)


class LocalFilesystemDocumentStorage:
    """Local object-storage analogue using server-derived paths and atomic writes."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def put(self, tenant_id: str, document_id: str, content: bytes) -> str:
        """Write with mode 0600, then atomically rename inside the storage root."""
        tenant_key = hashlib.sha256(tenant_id.encode()).hexdigest()[:24]
        storage_key = f"{tenant_key}/{document_id}.bin"
        destination = self._resolve_key(storage_key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(dir=destination.parent)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                os.fchmod(stream.fileno(), 0o600)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            Path(temporary_name).replace(destination)
        except Exception:
            Path(temporary_name).unlink(missing_ok=True)
            raise
        return storage_key

    def read(self, storage_key: str) -> bytes:
        return self._resolve_key(storage_key).read_bytes()

    def delete(self, storage_key: str) -> None:
        self._resolve_key(storage_key).unlink(missing_ok=True)

    def _resolve_key(self, storage_key: str) -> Path:
        candidate = (self._root / storage_key).resolve()
        if not candidate.is_relative_to(self._root):
            raise PermissionError("storage_key_outside_root")
        return candidate


def _normalize_text(text: str) -> str:
    """Normalize control characters and whitespace without altering factual text."""
    cleaned = "".join(
        character
        for character in text.replace("\r\n", "\n").replace("\r", "\n")
        if character in {"\n", "\t"} or ord(character) >= FIRST_PRINTABLE_CODEPOINT
    )
    return "\n".join(" ".join(line.split()) for line in cleaned.splitlines()).strip()
