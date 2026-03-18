"""
main.py - API Ebook Generator com Upload de Arquivos
Aceita: .txt e .docx → Gera .docx formatado profissional
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from docx import Document
import io
import os
from ebook_generator import EbookEngine

app = FastAPI(title="Ebook Generator API - Upload")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── HELPERS ────────────────────────────────────────────

def parse_txt(content: str) -> list:
    """
    Converte .txt em estrutura H1/H2/P automaticamente.
    Regras:
      - Linha com # → H1
      - Linha com ## → H2
      - Linha em branco → ignora
      - Resto → parágrafo
    """
    items = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            items.append({"type": "h2", "text": line[3:].strip()})
        elif line.startswith("# "):
            items.append({"type": "h1", "text": line[2:].strip()})
        else:
            items.append({"type": "p", "text": line})
    return items

def parse_docx(file_bytes: bytes) -> list:
    """
    Extrai texto do .docx mantendo hierarquia de estilos.
    Heading 1 → h1 | Heading 2 → h2 | Normal → p
    """
    doc = Document(io.BytesIO(file_bytes))
    items = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style = para.style.name
        if "Heading 1" in style:
            items.append({"type": "h1", "text": text})
        elif "Heading 2" in style:
            items.append({"type": "h2", "text": text})
        else:
            items.append({"type": "p", "text": text})
    return items

# ─── ENDPOINTS ──────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "message": "🚀 Ebook Generator rodando!",
        "endpoints": {
            "upload": "POST /upload-ebook/",
            "json": "POST /generate-ebook/"
        }
    }

@app.post("/upload-ebook/")
async def upload_ebook(
    file: UploadFile = File(...),
    title: str = Form(...),
    filename: str = Form("ebook-gerado.docx")
):
    """
    Recebe .txt ou .docx → gera eBook formatado → retorna .docx
    """
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".txt", ".docx"]:
            raise HTTPException(400, "Apenas arquivos .txt ou .docx são aceitos.")

        file_bytes = await file.read()

        # Parse conforme extensão
        if ext == ".txt":
            content_list = parse_txt(file_bytes.decode("utf-8", errors="ignore"))
        else:
            content_list = parse_docx(file_bytes)

        if not content_list:
            raise HTTPException(400, "Arquivo vazio ou sem conteúdo válido.")

        # Gera eBook
        engine = EbookEngine(title)
        temp_file = "temp_output.docx"
        engine.build_ebook(content_list, temp_file)

        with open(temp_file, "rb") as f:
            output = io.BytesIO(f.read())
        os.remove(temp_file)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro interno: {str(e)}")

@app.post("/generate-ebook/")
async def generate_ebook(request: dict):
    """Mantém endpoint JSON original"""
    try:
        title = request.get("title", "Ebook")
        content = request.get("content", [])
        filename = request.get("filename", "ebook.docx")
        engine = EbookEngine(title)
        temp_file = "temp_json.docx"
        engine.build_ebook(content, temp_file)
        with open(temp_file, "rb") as f:
            output = io.BytesIO(f.read())
        os.remove(temp_file)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(500, str(e))
