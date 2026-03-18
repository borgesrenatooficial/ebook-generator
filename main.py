"""
Nome do Script: main.py
Autor: Renato Borges
Versão: 1.1.0
Propósito: API FastAPI com gestão automática de arquivos temporários.
"""

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import os, uuid, logging
from ebook_generator import EbookEngine

app = FastAPI()
logger = logging.getLogger("uvicorn")

def cleanup(files: list):
    """Remove arquivos temporários do servidor."""
    for f in files:
        if os.path.exists(f): 
            os.remove(f)
            logger.info(f"Removido: {f}")

def parse_txt_safe(content_bytes: bytes) -> list:
    """Tenta UTF-8 e faz fallback para Latin-1."""
    try:
        text = content_bytes.decode('utf-8')
    except UnicodeDecodeError:
        text = content_bytes.decode('latin-1')
    
    parsed = []
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith("# "): parsed.append({"type": "h1", "text": line[2:]})
        elif line.startswith("## "): parsed.append({"type": "h2", "text": line[3:]})
        else: parsed.append({"type": "p", "text": line})
    return parsed

@app.post("/upload-ebook/")
async def upload_ebook(
    bg: BackgroundTasks,
    title: str = Form(...),
    filename: str = Form("ebook.docx"),
    file: UploadFile = File(...)
):
    uid = str(uuid.uuid4())
    in_file = f"in_{uid}_{file.filename}"
    out_file = f"out_{uid}.docx"

    try:
        content = await file.read()
        with open(in_file, "wb") as f: f.write(content)

        # Processamento
        if file.filename.endswith('.txt'):
            data = parse_txt_safe(content)
        else:
            # Para DOCX, no momento extraímos texto bruto (melhoria futura: manter estilos)
            from docx import Document as DocxReader
            doc = DocxReader(in_file)
            data = [{"type": "p", "text": p.text} for p in doc.paragraphs if p.text.strip()]

        engine = EbookEngine(title)
        engine.build_ebook(data, out_file)

        # Retorno via Stream
        file_handle = open(out_file, mode="rb")
        bg.add_task(cleanup, [in_file, out_file])

        return StreamingResponse(
            file_handle,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        cleanup([in_file, out_file])
        logger.error(f"Erro na API: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no processamento do Ebook.")

@app.get("/")
def health(): return {"status": "online", "engine": "EbookEngine 1.1.0"}
