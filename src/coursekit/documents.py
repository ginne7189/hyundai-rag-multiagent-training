import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentChunk:
    document_id: str
    document: str
    version: int
    page: int
    section: str
    text: str


def load_documents(directory: str | Path) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in sorted(Path(directory).glob("*.md")):
        content = path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        doc_id_match = re.search(r"^document_id:\s*(.+)$", content, re.MULTILINE)
        version_match = re.search(r"^version:\s*(\d+)$", content, re.MULTILINE)
        if not (title_match and doc_id_match and version_match):
            raise ValueError(f"Missing metadata in {path}")
        document = title_match.group(1).strip()
        document_id = doc_id_match.group(1).strip()
        version = int(version_match.group(1))
        sections = re.split(r"^##\s+", content, flags=re.MULTILINE)[1:]
        for section_block in sections:
            lines = section_block.strip().splitlines()
            heading = lines[0].strip()
            page_match = re.search(r"\[p\.(\d+)\]", heading)
            page = int(page_match.group(1)) if page_match else 0
            section = re.sub(r"\s*\[p\.\d+\]\s*", "", heading).strip()
            text = " ".join(line.strip() for line in lines[1:] if line.strip())
            if text:
                chunks.append(DocumentChunk(document_id, document, version, page, section, text))
    return chunks

