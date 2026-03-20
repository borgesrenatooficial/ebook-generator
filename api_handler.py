"""
Nome do Script: api_handler.py
Autor: Renato Borges
Data: 20 de Março de 2026
Versão: 3.1.0
Propósito: API de integração para o Plugin WP. Gerencia o fluxo completo:
           Recebe Manuscrito -> Processa IA (BNCC) -> Gera Capa -> Exporta DOCX 18pt.
"""

import logging
import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

# Importação dos módulos do repositório revisados
from main import EbookGenerator

# Configuração de Logging Profissional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EbookAPI")

app = FastAPI(title="Ebook Generator Pro API", version="3.1.0")

# Inicializa o orquestrador com o documento base da BNCC
CAMINHO_BNCC = "EBOOK-FEQ-BNCC-DA-COMPUTACAO-Professorrenato-com.pdf"
engine = EbookGenerator(CAMINHO_BNCC)

@app.post("/process-full-ebook/")
async def process_full_ebook(
    file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form("Renato Borges"),
    subtitle: Optional[str] = Form(None),
    color1: str = Form("#1e3c72"),
    color2: str = Form("#2a5298"),
    angle: int = Form(45),
    filename: str = Form("ebook_final.docx")
):
    """
    Endpoint principal que executa a esteira de produção completa.
    """
    temp_path = f"temp_{file.filename}"
    
    try:
        logger.info(f"Recebendo requisição para: {title}")
        
        # 1. Salva arquivo temporário para processamento
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Executa Etapa 1: Ingestão de Texto
        if not engine.executar_tela_1_upload(title, temp_path):
            raise HTTPException(status_code=400, detail="Erro ao processar manuscrito (DOCX/TXT).")

        # 3. Executa Etapa 2: Design de Capa
        engine.executar_tela_2_design(
            cores=[color1, color2],
            angulo=angle,
            autor=author,
            subtitulo=subtitle
        )

        # 4. Executa Etapa 3: Revisão Pedagógica IA
        # A IA aplica as diretrizes de Goiás e BNCC Computação
        engine.executar_tela_3_ia_revisao()

        # 5. Finalização e Exportação 18pt Mobile
        path_final = engine.finalizar_e_exportar(filename)
        
        if not path_final or not os.path.exists(path_final):
            raise HTTPException(status_code=500, detail="Erro na geração do arquivo DOCX.")

        logger.info(f"Ebook '{title}' gerado com sucesso. Enviando para WP...")
        
        return FileResponse(
            path=path_final, 
            filename=filename, 
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        logger.error(f"Falha crítica na API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Limpeza de arquivos temporários para manter o servidor Railway leve
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Autor: Renato Borges
