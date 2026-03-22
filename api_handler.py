"""
Nome do Script: api_handler.py
Autor: Renato Borges
Data: 22 de Março de 2026
Versão: 3.2.0
Propósito: API de Workflow para suportar as 3 telas do Plugin WordPress.
"""

import logging
import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSON_Response
from typing import Optional
from main import EbookGenerator #

app = FastAPI()
CAMINHO_BNCC = "EBOOK-FEQ-BNCC-DA-COMPUTACAO-Professorrenato-com.pdf"
engine = EbookGenerator(CAMINHO_BNCC) #

@app.post("/workflow/preview-capa")
async def preview_capa(
    title: str = Form(...),
    author: str = Form(...),
    color1: str = Form(...),
    color2: str = Form(...),
    angle: int = Form(...)
):
    """Gera um preview rápido da capa para a Tela 2."""
    path = engine.cover_factory.generate_cover(
        title=title, author=author, colors=[color1, color2], angle=angle
    ) #
    return FileResponse(path)

@app.post("/process-full-workflow/")
async def process_full_workflow(
    file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form(...),
    subtitle: Optional[str] = Form(None),
    color1: str = Form(...),
    color2: str = Form(...),
    angle: int = Form(...),
    filename: str = Form(...)
):
    """Executa a esteira completa: Ingestão -> Capa -> IA -> DOCX 18pt."""
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer) #

        # Etapa 1: Ingestão
        engine.executar_tela_1_upload(title, temp_path)
        
        # Etapa 2: Design
        engine.executar_tela_2_design([color1, color2], angle, author, subtitle)
        
        # Etapa 3: Revisão IA
        engine.executar_tela_3_ia_revisao()
        
        # Exportação Final 18pt
        path_final = engine.finalizar_e_exportar(filename)
        return FileResponse(path_final)
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)
