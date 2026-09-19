import pytest
from unittest.mock import AsyncMock, patch

from app.rag.loaders import (
    DocumentLoadError,
    load_csv,
    load_docx,
    load_file,
    load_txt,
    load_web,
)


def test_load_txt(tmp_path):
    p = tmp_path / "note.txt"
    p.write_text("Hello marketing world.")
    doc = load_txt(p)
    assert doc.source_type == "txt"
    assert "Hello marketing world." in doc.content
    assert doc.metadata["filename"] == "note.txt"


def test_load_txt_empty_raises(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_text("")
    with pytest.raises(DocumentLoadError):
        load_txt(p)


def test_load_csv(tmp_path):
    p = tmp_path / "campaigns.csv"
    p.write_text("name,goal\nSummer Sale,Increase revenue\n")
    doc = load_csv(p)
    assert doc.source_type == "csv"
    assert "Summer Sale" in doc.content
    assert doc.metadata["row_count"] == 1


def test_load_docx(tmp_path):
    from docx import Document

    p = tmp_path / "brand.docx"
    d = Document()
    d.add_paragraph("Our brand voice is bold and friendly.")
    d.save(p)

    doc = load_docx(p)
    assert doc.source_type == "docx"
    assert "bold and friendly" in doc.content


def test_load_file_unsupported_extension(tmp_path):
    p = tmp_path / "data.xyz"
    p.write_text("irrelevant")
    with pytest.raises(DocumentLoadError):
        load_file(p)


def test_load_file_dispatches_to_txt(tmp_path):
    p = tmp_path / "note.txt"
    p.write_text("Dispatch check.")
    doc = load_file(p)
    assert doc.source_type == "txt"


@pytest.mark.asyncio
async def test_load_web_success():
    html = "<html><body><script>ignored</script><p>Real content here.</p></body></html>"
    mock_response = AsyncMock()
    mock_response.text = html
    mock_response.raise_for_status = lambda: None

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        doc = await load_web("https://example.com/blog")
        assert doc.source_type == "web"
        assert "Real content here." in doc.content
        assert "ignored" not in doc.content
