"""
Nome do Script: main.py
Autor: Renato Borges
Data: 20 de Março de 2026
Versão: 2.7.0
Propósito: Orquestrador central do Ebook Generator.
           Integra Upload (T1), Design de Capa (T2) e Revisão Pedagógica IA (T3).
"""

import logging
from typing import List, Optional, Dict, Any

# Importação dos módulos especialistas
from manuscript_loader import ManuscriptProcessor
from brain_processor import BrainProcessor
from cover_generator import CoverGenerator

# Configuração de Logging Profissional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("ebook_flow.log"), logging.StreamHandler()]
)
logger = logging.getLogger("MainOrchestrator")

class EbookGenerator:
    """
    Controlador Sênior para automação de ebooks.
    Coordena a transição de dados entre as etapas de upload, design e IA.
    """

    def __init__(self, pdf_context_path: str):
        """
        Inicializa a pipeline com a base de conhecimento da BNCC.
        """
        self.loader = ManuscriptProcessor()
        self.brain = BrainProcessor(pdf_context_path)
        self.cover_factory = CoverGenerator()
        self.project_data: Dict[str, Any] = {}
        logger.info("Ebook Generator V2.7.0 operacional.")

    def etapa_1_upload(self, nome_ebook: str, arquivo_path: str) -> bool:
        """
        Processa o upload de arquivos DOCX ou TXT.
        """
        conteudo = self.loader.load(arquivo_path)
        if not conteudo:
            return False
        
        self.project_data = {
            "titulo": nome_ebook,
            "manuscrito": conteudo,
            "status": "UPLOAD_CONCLUIDO"
        }
        logger.info(f"Etapa 1 concluída para: {nome_ebook}")
        return True

    def etapa_2_design(self, cores: List[str], angulo: int, autor: str, subtitulo: Optional[str] = None):
        """
        Gera a capa do ebook com base nos inputs da Tela 2.
        """
        if "titulo" not in self.project_data:
            logger.error("Projeto não inicializado.")
            return

        path_capa = self.cover_factory.generate_cover(
            title=self.project_data["titulo"],
            author=autor,
            colors=cores,
            angle=angulo,
            subtitle=subtitulo,
            output_path=f"capa_{self.project_data['titulo'].replace(' ', '_')}.png"
        )
        self.project_data["capa_path"] = path_capa
        self.project_data["autor"] = autor
        logger.info(f"Etapa 2 concluída. Capa gerada em: {path_capa}")

    def etapa_3_revisao(self) -> str:
        """
        Aciona a IA para revisar o manuscrito com base no DC-GO/BNCC.
        """
        logger.info("Iniciando revisão pedagógica baseada na BNCC da Computação.")
        sugestoes = self.brain.analyze_pedagogy(self.project_data["manuscrito"])
        return self.brain.format_for_display(sugestoes)

# Autor: Renato Borges

if __name__ == "__main__":
    # Contexto: Documento Curricular para Goiás (DCGO) - Computação 
    BASE_CONHECIMENTO = "EBOOK-FEQ-BNCC-DA-COMPUTACAO-Professorrenato-com.pdf"
    
    app = EbookGenerator(BASE_CONHECIMENTO)
    
    # 1. Simulação Tela 1
    if app.etapa_1_upload("BNCC na Prática", "manuscrito.docx"):
        
        # 2. Simulação Tela 2 (Gradiente e Design)
        app.etapa_2_design(
            cores=["#6a11cb", "#2575fc"], 
            angulo=135, 
            autor="Renato Borges",
            subtitulo="Manual de Implementação para Professores"
        )
        
        # 3. Simulação Tela 3 (Sugestões da IA)
        painel_ia = app.etapa_3_revisao()
        print(painel_ia)
