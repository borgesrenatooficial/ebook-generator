"""
Nome do Script: api_handler.py
Autor: Renato Borges
Data: 22 de Março de 2026
Versão: 3.2.0
Propósito: API robusta para suportar o workflow de 3 etapas do WordPress.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from uuid import uuid4
import os
import shutil

# Importação dos módulos core revisados
from manuscript_loader import ManuscriptProcessor

app = FastAPI()
loader = ManuscriptProcessor()

# Dicionário em memória para demonstração (Em produção, use Redis ou Banco de Dados)
projects_db = {}

@app.post("/workflow/step1-upload")
async def step1_upload(
    title: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Recebe os dados da Tela 1: Nome do Ebook e Arquivo (DOCX/TXT).
    """
    project_id = str(uuid4())
    temp_path = f"storage/{project_id}_{file.filename}"
    
    # Criar pasta de storage se não existir
    os.makedirs("storage", exist_ok=True)

    try:
        # Salva o manuscrito temporariamente
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extrai o conteúdo para validação inicial
        content = loader.load(temp_path)
        
        if not content:
            raise HTTPException(status_code=400, detail="Arquivo inválido ou vazio.")

        # Armazena o estado inicial do projeto
        projects_db[project_id] = {
            "title": title,
            "raw_content": content,
            "file_path": temp_path,
            "status": "Aguardando Design"
        }

        return {
            "status": "success",
            "project_id": project_id,
            "message": "Upload concluído. Prossiga para a Etapa 2."
        }
    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

# Autor: Renato Borges
