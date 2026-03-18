"""
Nome do Script: main.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 1.1.0
Propósito: API FastAPI para interfaceamento com o Plugin WordPress.
"""

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import os, uuid, logging
from ebook_generator import EbookEngine
from docx import Document as DocxReader

app = FastAPI()
logger = logging.getLogger("uvicorn")

def remove_temp_files(*filepaths):
    """Garante que o storage do Railway não fique cheio."""
    for f in filepaths:
        if os.path.exists(f): os.remove(f)

def parse_txt(file_bytes: bytes) -> list:
    """Decodifica texto e identifica hierarquia Markdown (# e ##)."""
    try:
        content = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        content = file_bytes.decode('latin-1') # Fallback para arquivos Windows
    
    data = []
    for line in content.splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith("# "): data.append({"type": "h1", "text": line[2:]})
        elif line.startswith("## "): data.append({"type": "h2", "text": line[3:]})
        else: data.append({"type": "p", "text": line})
    return data

@app.post("/upload-ebook/")
async def handle_upload(
    bg: BackgroundTasks,
    title: str = Form(...),
    filename: str = Form("ebook.docx"),
    file: UploadFile = File(...)
):
    temp_id = str(uuid.uuid4())
    in_path = f"in_{temp_id}_{file.filename}"
    out_path = f"out_{temp_id}.docx"

    try:
        content = await file.read()
        with open(in_path, "wb") as f: f.write(content)

        # Seleção de Parser
        if file.filename.endswith('.txt'):
            parsed_content = parse_txt(content)
        else:
            doc = DocxReader(in_path)
            parsed_content = [{"type": "p", "text": p.text} for p in doc.paragraphs if p.text.strip()]

        # Geração
        engine = EbookEngine(title)
        engine.build(parsed_content, out_path)

        # Stream do resultado
        file_stream = open(out_path, mode="rb")
        bg.add_task(remove_temp_files, in_path, out_path)

        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        remove_temp_files(in_path, out_path)
        logger.error(f"Erro Crítico: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no processamento.")

@app.get("/")
def health(): return {"status": "ok"}"""
Nome do Script: main.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 1.1.0
Propósito: API FastAPI para interfaceamento com o Plugin WordPress.
"""

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import os, uuid, logging
from ebook_generator import EbookEngine
from docx import Document as DocxReader

app = FastAPI()
logger = logging.getLogger("uvicorn")

def remove_temp_files(*filepaths):
    """Garante que o storage do Railway não fique cheio."""
    for f in filepaths:
        if os.path.exists(f): os.remove(f)

def parse_txt(file_bytes: bytes) -> list:
    """Decodifica texto e identifica hierarquia Markdown (# e ##)."""
    try:
        content = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        content = file_bytes.decode('latin-1') # Fallback para arquivos Windows
    
    data = []
    for line in content.splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith("# "): data.append({"type": "h1", "text": line[2:]})
        elif line.startswith("## "): data.append({"type": "h2", "text": line[3:]})
        else: data.append({"type": "p", "text": line})
    return data

@app.post("/upload-ebook/")
async def handle_upload(
    bg: BackgroundTasks,
    title: str = Form(...),
    filename: str = Form("ebook.docx"),
    file: UploadFile = File(...)
):
    temp_id = str(uuid.uuid4())
    in_path = f"in_{temp_id}_{file.filename}"
    out_path = f"out_{temp_id}.docx"

    try:
        content = await file.read()
        with open(in_path, "wb") as f: f.write(content)

        # Seleção de Parser
        if file.filename.endswith('.txt'):
            parsed_content = parse_txt(content)
        else:
            doc = DocxReader(in_path)
            parsed_content = [{"type": "p", "text": p.text} for p in doc.paragraphs if p.text.strip()]

        # Geração
        engine = EbookEngine(title)
        engine.build(parsed_content, out_path)

        # Stream do resultado
        file_stream = open(out_path, mode="rb")
        bg.add_task(remove_temp_files, in_path, out_path)

        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        remove_temp_files(in_path, out_path)
        logger.error(f"Erro Crítico: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no processamento.")

@app.get("/")
def health(): return {"status": "ok"}
