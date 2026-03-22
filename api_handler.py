"""
Nome do Script: api_handler.py
Autor: Renato Borges
Versão: 3.3.0
Propósito: API com suporte completo à Etapa 3 (Diagramação IA e Exportação).
"""

import logging
import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

# Importação do orquestrador
from main import EbookGenerator

app = FastAPI(title="Ebook Generator Pro API")

# Inicializa o motor com o PDF de contexto
CAMINHO_BNCC = "EBOOK-FEQ-BNCC-DA-COMPUTACAO-Professorrenato-com.pdf"
engine = EbookGenerator(CAMINHO_BNCC)

@app.post("/workflow/ai-layout-suggestion")
async def ai_layout_suggestion(text: str = Form(...)):
    """
    Atende ao botão 'Revisão por IA' do Painel Esquerdo.
    """
    try:
        # Chama a IA de Layout para otimizar o texto
        optimized = engine.brain.optimize_layout(text)
        return {"optimized_text": optimized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-full-ebook/")
async def process_full_ebook(
    file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form(...),
    subtitle: Optional[str] = Form(None),
    color1: str = Form("#1e3c72"),
    color2: str = Form("#2a5298"),
    angle: int = Form(45),
    filename: str = Form("ebook.docx"),
    content_final: Optional[str] = Form(None) # Recebe o texto do editor WYSIWYG
):
    """
    Gera o DOCX final com 18pt e layout mobile.
    """
    temp_path = f"temp_{file.filename}"
    try:
        # 1. Salva arquivo temporário
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Ingestão (Tela 1)
        engine.executar_tela_1_upload(title, temp_path)

        # 3. Design (Tela 2)
        engine.executar_tela_2_design([color1, color2], angle, author, subtitle)

        # 4. Finalização (Tela 3)
        # Se o usuário editou no WYSIWYG, usamos esse conteúdo
        conteudo_para_exportar = content_final if content_final else engine.project_data["conteudo_bruto"]
        
        # Aplica a diagramação final
        engine.project_data["conteudo_otimizado"] = engine.brain.optimize_layout(conteudo_para_exportar)

        # 5. Exportação DOCX 18pt
        path_final = engine.finalizar_e_exportar(filename)
        
        return FileResponse(path_final, filename=filename)

    except Exception as e:
        logging.error(f"Erro na Engine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Autor: Renato Borges
