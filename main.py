"""
Nome do Script: main.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 1.1.0
Propósito: API REST para processamento de arquivos e geração de eBooks.
"""

import os
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from ebook_engine import EbookEngine
from docx import Document as DocxReader

# Configurações Iniciais
app = FastAPI(title="Ebook Generator API")
logger = logging.getLogger("uvicorn")

def cleanup_file(filepath: str):
    """Remove o arquivo temporário do disco após o envio."""
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"Arquivo temporário removido: {filepath}")

def parse_txt(content: str) -> list:
    """Faz o parse de strings .txt seguindo regras de Markdown simplificado (# e ##)."""
    lines = content.split('\n')
    parsed_data = []
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if line.startswith("# "):
            parsed_data.append({"type": "h1", "text": line[2:]})
        elif line.startswith("## "):
            parsed_data.append({"type": "h2", "text": line[3:]})
        else:
            parsed_data.append({"type": "p", "text": line})
    return parsed_data

def parse_docx(file_path: str) -> list:
    """Extrai estrutura h1, h2 e p de um arquivo .docx existente."""
    doc = DocxReader(file_path)
    parsed_data = []
    for para in doc.paragraphs:
        style = para.style.name.lower()
        text = para.text.strip()
        if not text: continue
        
        if "heading 1" in style:
            parsed_data.append({"type": "h1", "text": text})
        elif "heading 2" in style:
            parsed_data.append({"type": "h2", "text": text})
        else:
            parsed_data.append({"type": "p", "text": text})
    return parsed_data

@app.get("/")
async def health_check():
    """Endpoint de verificação de integridade."""
    return {"status": "online", "message": "Ebook Generator API rodando!", "version": "1.1.0"}

@app.post("/upload-ebook/")
async def upload_ebook(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    filename: str = Form("ebook.docx"),
    file: UploadFile = File(...)
):
    """
    Recebe arquivo, processa e retorna o .docx formatado.
    """
    temp_input = f"input_{uuid.uuid4()}_{file.filename}"
    temp_output = f"output_{uuid.uuid4()}.docx"
    
    try:
        # Salva arquivo enviado pelo usuário
        with open(temp_input, "wb") as buffer:
            content_bytes = await file.read()
            buffer.write(content_bytes)

        # Determina o parser
        if file.filename.endswith('.txt'):
            content_str = content_bytes.decode("utf-8")
            content_list = parse_txt(content_str)
        else:
            content_list = parse_docx(temp_input)

        # Gera o novo eBook
        engine = EbookEngine(title)
        engine.build_ebook(content_list, temp_output)

        # Retorna o arquivo como Stream
        file_handle = open(temp_output, mode="rb")
        
        # Agenda limpeza dos arquivos temporários
        background_tasks.add_task(cleanup_file, temp_input)
        background_tasks.add_task(cleanup_file, temp_output)

        return StreamingResponse(
            file_handle,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Erro no processamento: {str(e)}")
        # Garante limpeza em caso de erro
        cleanup_file(temp_input)
        cleanup_file(temp_output)
        return JSONResponse(status_code=500, content={"error": "Falha ao gerar eBook."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
