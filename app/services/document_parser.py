from pathlib import Path

import fitz
from docx import Document


class DocumentParser:
    def parse(self, file_path: str) -> str:
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == ".pdf":
            return self._parse_pdf(path)

        if extension == ".docx":
            return self._parse_docx(path)

        if extension in {".txt", ".md", ".markdown"}:
            return self._parse_text(path)

        raise ValueError(f"Unsupported file type for parsing: {extension}")

    def _parse_pdf(self, path: Path) -> str:
        texts: list[str] = []

        with fitz.open(path) as pdf:
            for page in pdf:
                page_text = page.get_text("text")
                if page_text:
                    texts.append(page_text)

        return "\n".join(texts).strip()

    def _parse_docx(self, path: Path) -> str:
        document = Document(path)
        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs).strip()

    def _parse_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore").strip()