"""
Nome do Script: main.py
Autor: Renato Borges
Versão: 1.2.5
Propósito: API FastAPI resiliente com suporte a IA e correção de concorrência.
"""

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import os, uuid, logging, httpx
from ebook_generator import EbookEngine

app = FastAPI()
logger = logging.getLogger("uvicorn")

# Variável de Ambiente para segurança
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

async def review_text_with_ai(text: str) -> str:
    """Revisão via Perplexity com tratamento de exceção para evitar Erro 500."""
    if not PERPLEXITY_API_KEY:
        return text
    
    prompt = (
        "Reescreva para leitura em celular (mobile-first). "
        "Mantenha as marcações # (H1) e ## (H2). "
        "Parágrafos de no máximo 4 linhas. Texto:\n\n" + text
    )

    try:
        async with httpx.AsyncClient(timeout=80.0) as client:
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
        logger.error(f"IA Error: {e}")
        return text

def cleanup(files: list):
    for f in files:
        if os.path.exists(f): os.remove(f)

@app.post("/upload-ebook/")
async def upload_ebook(
    bg: BackgroundTasks,
    title: str = Form(...),
    filename: str = Form("ebook.docx"),
    file: UploadFile = File(...)
):
    uid = str(uuid.uuid4())
    in_file, out_file = f"in_{uid}.tmp", f"out_{uid}.docx"

    try:
        # 1. Salva arquivo de entrada
        content = await file.read()
        with open(in_file, "wb") as f: f.write(content)

        # 2. Processamento (TXT com IA ou DOCX direto)
        if file.filename.endswith('.txt'):
            raw_text = content.decode('utf-8', errors='replace')
            final_text = await review_text_with_ai(raw_text)
            
            # Converte texto processado para lista de objetos para a Engine
            data = []
            for line in final_text.splitlines():
                line = line.strip()
                if not line: continue
                if line.startswith("# "): data.append({"type": "h1", "text": line[2:]})
                elif line.startswith("## "): data.append({"type": "h2", "text": line[3:]})
                else: data.append({"type": "p", "text": line})
        else:
            from docx import Document as DocxReader
            doc = DocxReader(in_file)
            data = [{"type": "p", "text": p.text} for p in doc.paragraphs if p.text.strip()]

        # 3. Geração do Ebook (Garante que a Engine use build_ebook)
        engine = EbookEngine(title)
        engine.build_ebook(data, out_file) # Verifique se o nome na Engine é este!

        # 4. Envio do arquivo
        def iterfile():
            with open(out_file, mode="rb") as f:
                yield from f

        bg.add_task(cleanup, [in_file, out_file])
        return StreamingResponse(
            iterfile(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        cleanup([in_file, out_file])
        logger.error(f"FAIL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
