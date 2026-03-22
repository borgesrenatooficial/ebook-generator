"""
Nome do Script: main.py
Autor: Renato Borges
Data: 22 de Março de 2026
Versão: 3.0.0
Propósito: Orquestrador central focado em Layout Mobile-First. 
           Integra Ingestão, Design de Capa e IA de Diagramação Estrutural.
"""

import logging
import os
from typing import List, Optional, Dict, Any

# Importação dos módulos especialistas da pipeline
from manuscript_loader import ManuscriptProcessor
from brain_processor import BrainProcessor
from cover_generator import CoverGenerator
from docx_export import DocxExporter

# Configuração de Logging Profissional para monitoramento de workflow
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ebook_workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MainOrchestrator")

class EbookGenerator:
    """
    Controlador do Workflow de 3 Etapas. 
    Foco: Transformar manuscritos em DOCX 18pt sem erros de quebra estrutural.
    """

    def __init__(self, context_pdf_path: Optional[str] = None):
        """
        Inicializa o motor com foco em otimização de layout.
        """
        self.loader = ManuscriptProcessor()
        self.brain = BrainProcessor(context_pdf_path) # IA de Layout
        self.cover_factory = CoverGenerator()
        self.exporter = DocxExporter()
        
        # Armazenamento de estado do projeto
        self.project_data: Dict[str, Any] = {
            "titulo": "",
            "subtitulo": None,
            "autor": "Renato Borges",
            "conteudo_bruto": "",
            "conteudo_otimizado": "",
            "capa_path": "",
            "status": "INICIALIZADO"
        }
        logger.info("Ebook Generator V3.0.0 iniciado com foco em Diagramação Mobile.")

    def executar_tela_1_upload(self, titulo: str, arquivo_path: str) -> bool:
        """Etapa 1: Ingestão e Identificação do Manuscrito."""
        logger.info(f"Executando Etapa 1: Upload de '{titulo}'")
        texto = self.loader.load(arquivo_path)
        
        if not texto:
            logger.error("Falha na ingestão do arquivo.")
            return False
        
        self.project_data["titulo"] = titulo
        self.project_data["conteudo_bruto"] = texto
        self.project_data["status"] = "TELA_1_OK"
        return True

    def executar_tela_2_design(self, cores: List[str], angulo: int, autor: str, subtitulo: Optional[str] = None):
        """Etapa 2: Geração da Identidade Visual da Capa."""
        logger.info("Executando Etapa 2: Design de Capa.")
        self.project_data["autor"] = autor
        self.project_data["subtitulo"] = subtitulo
        
        path_gerado = self.cover_factory.generate_cover(
            title=self.project_data["titulo"],
            author=autor,
            colors=cores,
            angle=angulo,
            subtitle=subtitulo,
            output_path=f"capa_{self.project_data['titulo'].replace(' ', '_')}.png"
        )
        self.project_data["capa_path"] = path_gerado
        self.project_data["status"] = "TELA_2_OK"

    def executar_tela_3_diagramacao_ia(self) -> str:
        """Etapa 3: IA de Otimização Estrutural (Anti-Quebra)."""
        logger.info("Executando Etapa 3: IA de Diagramação.")
        texto_original = self.project_data["conteudo_bruto"]
        
        # A IA agora divide parágrafos densos e garante respiro visual
        texto_otimizado = self.brain.optimize_layout(texto_original)
        
        self.project_data["conteudo_otimizado"] = texto_otimizado
        self.project_data["status"] = "TELA_3_OK"
        
        return self.brain.format_for_display([])

    def finalizar_e_exportar(self, filename: Optional[str] = None) -> Optional[str]:
        """Finalização e Exportação para DOCX 18pt."""
        logger.info("Finalizando projeto e exportando para DOCX Mobile-First.")
        nome_arquivo = filename or f"{self.project_data['titulo'].replace(' ', '_')}_Final.docx"
        
        # Prioriza o conteúdo otimizado pela IA de Layout
        conteudo_final = self.project_data.get("conteudo_otimizado") or self.project_data.get("conteudo_bruto")
        
        path_final = self.exporter.gerar_ebook_docx(
            titulo=self.project_data["titulo"],
            autor=self.project_data["autor"],
            conteudo=conteudo_final,
            output_path=nome_arquivo,
            subtitulo=self.project_data["subtitulo"]
        )
        
        if path_final:
            logger.info(f"Ebook exportado com sucesso: {path_final}")
            self.project_data["status"] = "CONCLUIDO"
        
        return path_final

# Autor: Renato Borges

if __name__ == "__main__":
    # O PDF é opcional na V3.0 (IA focada em estrutura)
    app = EbookGenerator()
    
    # Simulação do Workflow Completo
    if app.executar_tela_1_upload("Ebook Mobile Expert", "manuscrito.docx"):
        app.executar_tela_2_design(
            cores=["#1e3c72", "#2a5298"], 
            angulo=45, 
            autor="Renato Borges"
        )
        
        status_ia = app.executar_tela_3_diagramacao_ia()
        print(status_ia)
        
        app.finalizar_e_exportar()
