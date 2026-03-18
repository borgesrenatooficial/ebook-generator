"""
Nome do Script: main.py
Autor: Renato Borges
Versão: 1.2.8
Propósito: API FastAPI resiliente com tratamento de exceções global.
"""

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import os, uuid, logging, httpx
from ebook_generator import EbookEngine

app = FastAPI()
logger = logging.getLogger("uvicorn")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

async def review_text_with_ai(text: str) -> str:
    """Revisão via Perplexity. Se falhar, retorna o texto original."""
    if not PERPLEXITY_API_KEY:
        return text
    
    prompt = (
        "Reescreva para leitura em celular (mobile-first) conforme as diretrizes: "
        "1. Divida em parágrafos de 3 a 5 linhas. "
        "2. Mantenha marcas # (H1) e ## (H2). Texto:\n\n" + text
    )

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"},
                json={
                    "model": "pplx-7b-online",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content']
            return text
    except Exception as e:
        logger.error(f"IA Timeout ou Erro: {e}")
        return text

def parse_content(text: str) -> list:
    """Transforma texto em lista de blocos H1, H2 e P."""
    data = []
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith("# "): data.append({"type": "h1", "text": line[2:]})
        elif line.startswith("## "): data.append({"type": "h2", "text": line[3:]})
        else: data.append({"type": "p", "text": line})
    return data

@app.post("/upload-ebook/")
async def upload_ebook(
    bg: BackgroundTasks, 
    title: str = Form(...), 
    filename: str = Form(...), 
    file: UploadFile = File(...)
):
    uid = str(uuid.uuid4())
    in_file, out_file = f"in_{uid}.tmp", f"out_{uid}.docx"
    
    try:
        content_bytes = await file.read()
        with open(in_file, "wb") as f:
            f.write(content_bytes)

        if file.filename.endswith('.txt'):
            raw_text = content_bytes.decode('utf-8', errors='replace')
            # Chama IA mas garante fallback
            final_text = await review_text_with_ai(raw_text)
            data = parse_content(final_text)
        else:
            from docx import Document as DocxReader
            doc = DocxReader(in_file)
            data = [{"type": "p", "text": p.text} for p in doc.paragraphs if p.text.strip()]

        # Geração do Ebook
        engine = EbookEngine(title)
        engine.build_ebook(data, out_file)

        # Retorno do Stream
        def iterfile():
            with open(out_file, mode="rb") as f:
                yield from f

        bg.add_task(lambda: [os.remove(f) for f in [in_file, out_file] if os.path.exists(f)])
        
        return StreamingResponse(
            iterfile(), 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        if os.path.exists(in_file): os.remove(in_file)
        logger.error(f"ERRO 500 DETECTADO: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Falha interna: {str(e)}")
