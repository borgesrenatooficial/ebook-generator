"""
Nome do Script: main.py
Autor: Renato Borges
Versão: 1.2.6
Propósito: Debug agressivo para eliminar Erro 500.
"""

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import os, uuid, logging, httpx
from ebook_generator import EbookEngine

app = FastAPI()
logger = logging.getLogger("uvicorn")

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

@app.post("/upload-ebook/")
async def upload_ebook(
    bg: BackgroundTasks,
    title: str = Form(...),
    filename: str = Form("ebook.docx"),
    file: UploadFile = File(...)
):
    uid = str(uuid.uuid4())
    in_file = f"in_{uid}.tmp"
    out_file = f"out_{uid}.docx"

    try:
        # LOG DE DEPURAÇÃO 1
        logger.info(f"Recebendo arquivo: {file.filename} para o título: {title}")
        
        content = await file.read()
        if not content:
            raise ValueError("O conteúdo do arquivo está vazio.")

        with open(in_file, "wb") as f:
            f.write(content)

        # LOG DE DEPURAÇÃO 2
        logger.info("Iniciando processamento de texto...")

        if file.filename.endswith('.txt'):
            text = content.decode('utf-8', errors='replace')
            # Bypass simples de IA se houver erro na chamada
            try:
                if PERPLEXITY_API_KEY:
                    # Chamada simplificada para teste
                    data = [{"type": "p", "text": text}] 
                else:
                    from main import parse_txt_safe # Supondo que a função esteja aqui
                    data = parse_txt_safe(content)
            except:
                data = [{"type": "p", "text": text}]
        else:
            from docx import Document as DocxReader
            doc = DocxReader(in_file)
            data = [{"type": "p", "text": p.text} for p in doc.paragraphs if p.text.strip()]

        # LOG DE DEPURAÇÃO 3
        logger.info(f"Gerando Word com {len(data)} blocos de texto.")
        
        engine = EbookEngine(title)
        # Sincronização obrigatória com o nome do método na engine
        engine.build_ebook(data, out_file) 

        # Entrega do arquivo
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
        # SE DER ERRO, REMOVE OS ARQUIVOS E GERA LOG DETALHADO
        if os.path.exists(in_file): os.remove(in_file)
        if os.path.exists(out_file): os.remove(out_file)
        logger.error(f"DETALHE DO ERRO 500: {str(e)}")
        # Retorna o erro exato para você ver no navegador
        raise HTTPException(status_code=500, detail=f"Erro Técnico: {str(e)}")
