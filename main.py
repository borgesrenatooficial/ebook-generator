"""
main.py - API Web para Ebook Generator com FastAPI
Compatível com Railway/Render - Deploy automático
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import io
import os
from ebook_generator import EbookEngine  # Importa sua classe original

app = FastAPI(
    title="Ebook Generator API",
    description="Gera eBooks profissionais em .docx com H1/H2/Body + paginação",
    version="1.0.0"
)

class ContentItem(BaseModel):
    """Estrutura para cada item de conteúdo"""
    type: str  # 'h1', 'h2' ou 'p'
    text: str
    break_page: bool = False

@app.get("/")
async def root():
    """Página inicial"""
    return {
        "message": "🚀 Ebook Generator rodando!",
        "docs": "/docs",  # Swagger UI automática
        "usage": "POST /generate-ebook/ com JSON: [{'type':'h1','text':'Título'}]"
    }

@app.post("/generate-ebook/")
async def generate_ebook(
    title: str,
    content: List[ContentItem],
    filename: str = "ebook.docx"
):
    """
    GERA O EBOOK!
    - title: Título principal
    - content: Lista com type/text
    - filename: Nome do arquivo baixado
    """
    try:
        # Converte Pydantic para formato do seu EbookEngine
        content_list = []
        for item in content:
            content_list.append({
                "type": item.type,
                "text": item.text,
                "break_page": item.break_page
            })
        
        # Usa sua classe original!
        engine = EbookEngine(title)
        temp_filename = "temp_ebook.docx"
        engine.build_ebook(content_list, temp_filename)
        
        # Envia arquivo para download
        with open(temp_filename, "rb") as f:
            file_content = io.BytesIO(f.read())
        
        # Limpa arquivo temporário
        os.remove(temp_filename)
        
        return StreamingResponse(
            file_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@app.get("/docs")
async def docs_redirect():
    """Redireciona para Swagger UI"""
    return {"message": "Acesse /docs no navegador para interface interativa!"}
