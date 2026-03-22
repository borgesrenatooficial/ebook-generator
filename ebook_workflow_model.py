"""
Nome do Script: ebook_workflow_model.py
Autor: Renato Borges
Data: 22 de Março de 2026
Versão: 1.0.0
Propósito: Modelo de dados para gerenciar o estado das 3 etapas da interface.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class EbookProject(BaseModel):
    # Tela 1: Identificação
    project_id: str
    ebook_name: str
    raw_manuscript: str  # Texto extraído do DOCX/TXT
    
    # Tela 2: Design
    cover_title: str
    cover_subtitle: Optional[str] = None
    author_name: str
    primary_color: str = "#1e3c72"
    secondary_color: str = "#2a5298"
    gradient_angle: int = 45
    
    # Tela 3: Formatação & IA
    current_content_version: str
    ai_suggestions: List[dict] = []
    font_family: str = "Arial"
    font_size: int = 18  # Padronizado para Mobile 18pt

# Autor: Renato Borges
