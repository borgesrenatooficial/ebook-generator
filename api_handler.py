"""
Nome do Script: api_handler.py
Autor: Renato Borges
Versão: 3.6.0
Propósito: API com suporte completo à extração em tempo real, 
           diagramação por IA e exportação mobile (18pt).
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

# Inicializa o motor
CAMINHO_BNCC = "EBOOK-FEQ-BNCC-DA-COMPUTACAO-Professorrenato-com.pdf"
engine = EbookGenerator(CAMINHO_BNCC)

@app.post("/workflow/extract-text")
async def extract_text(file: UploadFile = File(...), title: str = Form(...)):
    """
    NOVO: Rota para extração imediata (Etapa 1 -> Visualizador).
    Resolve o problema do texto não aparecer no painel central.
    """
    temp_path = f"extract_{file.filename}"
    try:
        # 1. Salva temporário para leitura
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Extrai o texto usando o loader
        raw_text = engine.loader.load(temp_path)
        
        if not raw_text:
            raise ValueError("Não foi possível extrair texto do arquivo.")

        # 3. IA de Layout prepara o respiro inicial
        optimized_text = engine.brain.optimize_layout(raw_text)
        
        # 4. Converte para HTML simples para o editor WYSIWYG
        html_formatted = "".join([f"<p>{line}</p>" for line in optimized_text.split('\n') if line.strip()])
        final_html = f"<h1>{title}</h1>{html_formatted}"
        
        return {"html": final_html}
    
    except Exception as e:
        logging.error(f"Erro na extração: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/workflow/ai-layout-suggestion")
async def ai_layout_suggestion(text: str = Form(...)):
    """
    Atende ao botão 'Revisão por IA' do Painel Esquerdo.
    """
    try:
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
    content_final: Optional[str] = Form(None) 
):
    """
    Gera o DOCX final com 18pt consumindo o HTML do editor.
    """
    temp_path = f"final_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ingestão e Design
        engine.executar_tela_1_upload(title, temp_path)
        engine.executar_tela_2_design([color1, color2], angle, author, subtitle)

        # Se houver conteúdo do editor (HTML), limpamos as tags para a exportação DOCX
        # Nota: O docx_export deve ser capaz de lidar com quebras simples ou tags
        conteudo_para_exportar = content_final if content_final else engine.project_data["conteudo_bruto"]
        
        # Otimização final de respiro
        engine.project_data["conteudo_otimizado"] = engine.brain.optimize_layout(conteudo_para_exportar)

        path_final = engine.finalizar_e_exportar(filename)
        return FileResponse(path_final, filename=filename)

    except Exception as e:
        logging.error(f"Erro na exportação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Autor: Renato Borges
