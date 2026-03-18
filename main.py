"""
Nome do Script: main.py
Autor: Renato Borges
Versão: 1.2.7
Propósito: API FastAPI integrada com Perplexity e fallback resiliente.
"""

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import os, uuid, logging, httpx
from ebook_generator import EbookEngine

app = FastAPI()
logger = logging.getLogger("uvicorn")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

async def review_text_with_ai(text: str) -> str:
    """Solicita revisão para leitura mobile e quebra de parágrafos[cite: 27, 31]."""
    if not PERPLEXITY_API_KEY: return text
    
    prompt = (
        "Reescreva para leitura em celular[cite: 30]. "
        "Divida o texto em parágrafos de 3 a 5 linhas[cite: 31]. "
        "Mantenha marcas # e ##[cite: 33]. Texto:\n\n" + text
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"},
                json={
                    "model": "pplx-7b-online",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            return resp.json()['choices'][0]['message']['content'] if resp.status_code == 200 else text
    except: return text

@app.post("/upload-ebook/")
async def upload_ebook(bg: BackgroundTasks, title: str = Form(...), filename: str = Form(...), file: UploadFile = File(...)):
    uid = str(uuid.uuid4())
    in_file, out_file = f"in_{uid}.tmp", f"out_{uid}.docx"
    try:
        content = await file.read()
        with open(in_file, "wb") as f: f.write(content)

        # Processamento [cite: 33]
        if file.filename.endswith('.txt'):
            raw_text = content.decode('utf-8', errors='replace')
            final_text = await review_text_with_ai(raw_text)
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

        engine = EbookEngine(title)
        engine.build_ebook(data, out_file)

        bg.add_task(lambda: [os.remove(f) for f in [in_file, out_file] if os.path.exists(f)])
        return StreamingResponse(open(out_file, "rb"), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    except Exception as e:
        if os.path.exists(in_file): os.remove(in_file)
        raise HTTPException(status_code=500, detail=str(e))
