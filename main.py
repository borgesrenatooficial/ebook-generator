"""
main.py - API Web para Ebook Generator com FastAPI
Compatível com Railway/Render - Deploy automático
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import io
import os
from ebook_generator import EbookEngine

app = FastAPI(title="Ebook Generator")

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ContentItem(BaseModel):
    type: str
    text: str
    break_page: bool = False

@app.get("/")
async def root():
    return {"message": "🚀 Ebook Generator rodando!", "endpoint": "/generate-ebook/"}

@app.post("/generate-ebook/")
async def generate_ebook(request: dict):  # Recebe TUDO no body JSON
    """
    Recebe: {"title": "...", "content": [...], "filename": "..."}
    """
    try:
        title = request.get("title", "Ebook Sem Título")
        content = request.get("content", [])
        filename = request.get("filename", "ebook.docx")
        
        if not content:
            raise ValueError("Content é obrigatório")
        
        # Converte para formato do EbookEngine
        content_list = [{"type": c["type"], "text": c["text"], "break_page": c.get("break_page", False)} for c in content]
        
        engine = EbookEngine(title)
        temp_filename = "temp.docx"
        engine.build_ebook(content_list, temp_filename)
        
        with open(temp_filename, "rb") as f:
            file_content = io.BytesIO(f.read())
        os.remove(temp_filename)
        
        return StreamingResponse(
            file_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(500, f"Erro: {str(e)}")

@app.get("/test")
async def test():
    """Endpoint de teste simples"""
    return {"status": "OK", "ready": True}


# Redireciona /docs para raiz (temporário)
@app.get("/docs")
@app.get("/redoc")
async def docs_redirect():
    return {"message": "Use POST /generate-ebook/ | Teste via curl/Postman | /docs em breve"}
