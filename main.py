"""
main.py - API Web para Ebook Generator com FastAPI
Compatível com Railway/Render - Deploy automático
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import io
import os
from ebook_generator import EbookEngine

app = FastAPI(
    title="Ebook Generator API",
    description="Gera eBooks .docx profissionais",
    version="1.0.1"
)

# CORS para front HTML
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContentItem(BaseModel):
    type: str
    text: str
    break_page: bool = False

@app.get("/")
async def root():
    return {
        "message": "🚀 Ebook Generator rodando!",
        "api": "/generate-ebook/",
        "docs": "/docs", 
        "test_here": "Use /generate-ebook/ diretamente"
    }

@app.post("/generate-ebook/")
async def generate_ebook(title: str, content: List[ContentItem], filename: str = "ebook.docx"):
    try:
        content_list = [{"type": c.type, "text": c.text, "break_page": c.break_page} for c in content]
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
        raise HTTPException(500, str(e))

# Redireciona /docs para raiz (temporário)
@app.get("/docs")
@app.get("/redoc")
async def docs_redirect():
    return {"message": "Use POST /generate-ebook/ | Teste via curl/Postman | /docs em breve"}
