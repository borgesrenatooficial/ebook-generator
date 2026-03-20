"""
Nome do Script: main.py
Autor: Renato Borges
Data: 20 de Março de 2026
Versão: 2.8.0
Propósito: Orquestrador central do Ebook Generator. Integra todas as fases:
           1. Ingestão de Manuscritos (DOCX/TXT)
           2. Geração de Design de Capa (Gradientes/Tipografia)
           3. Revisão Pedagógica com IA (Baseada no DC-GO/BNCC Computação)
           4. Exportação Final de Documento (DOCX)
"""

import logging
import os
from typing import List, Optional, Dict, Any

# Importação dos módulos especialistas desenvolvidos na pipeline
from manuscript_loader import ManuscriptProcessor
from brain_processor import BrainProcessor
from cover_generator import CoverGenerator
from docx_export import DocxExporter

# Configuração de Logging Profissional para monitoramento de processos de trading de dados
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ebook_generator_core.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MainOrchestrator")

class EbookGenerator:
    """
    Controlador Sênior para automação e geração de materiais didáticos.
    Gerencia o estado do projeto através das três etapas da interface.
    """

    def __init__(self, pdf_context_path: str):
        """
        Inicializa o motor de geração com o contexto pedagógico necessário.
        
        Args:
            pdf_context_path (str): Caminho para o PDF da BNCC da Computação (DC-GO).
        """
        self.loader = ManuscriptProcessor()
        self.brain = BrainProcessor(pdf_context_path)
        self.cover_factory = CoverGenerator()
        self.exporter = DocxExporter()
        
        # Armazenamento de estado do projeto ativo
        self.project_data: Dict[str, Any] = {
            "titulo": "",
            "subtitulo": None,
            "autor": "Renato Borges",
            "manuscrito_original": "",
            "manuscrito_revisado": "",
            "capa_path": "",
            "status": "INICIALIZADO"
        }
        logger.info(f"Ebook Generator V2.8.0 iniciado. Contexto: {os.path.basename(pdf_context_path)}")

    def executar_tela_1_upload(self, nome_ebook: str, arquivo_path: str) -> bool:
        """
        Processa o upload inicial e extração de texto (DOCX/TXT).
        """
        logger.info(f"Executando Etapa 1: Upload de '{nome_ebook}'")
        conteudo = self.loader.load(arquivo_path)
        
        if not conteudo:
            logger.error("Falha na ingestão do arquivo. Abortando processo.")
            return False
        
        self.project_data["titulo"] = nome_ebook
        self.project_data["manuscrito_original"] = conteudo
        self.project_data["status"] = "UPLOAD_CONCLUIDO"
        return True

    def executar_tela_2_design(self, cores: List[str], angulo: int, autor: str, subtitulo: Optional[str] = None):
        """
        Gera a identidade visual da capa conforme inputs da interface.
        """
        logger.info("Executando Etapa 2: Geração de Design da Capa.")
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
        self.project_data["status"] = "DESIGN_CONCLUIDO"

    def executar_tela_3_ia_revisao(self) -> str:
        """
        Processa o manuscrito com o cérebro de IA baseado no PDF da BNCC.
        Retorna as sugestões formatadas para o painel de revisão.
        """
        logger.info("Executando Etapa 3: Revisão Pedagógica IA.")
        manuscrito = self.project_data["manuscrito_original"]
        
        # O BrainProcessor analisa termos como 'Mundo Digital' e 'Pensamento Computacional'
        sugestoes_analise = self.brain.analyze_pedagogy(manuscrito)
        
        # Simulamos a aplicação automática para este exemplo, mas na interface o usuário 'Aceita'
        self.project_data["manuscrito_revisado"] = manuscrito # Aqui entraria a lógica de 'Accept'
        self.project_data["status"] = "REVISAO_IA_CONCLUIDA"
        
        return self.brain.format_for_display(sugestoes_analise)

    def finalizar_e_exportar(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Consolida o projeto final em um arquivo DOCX.
        """
        logger.info("Finalizando projeto e exportando para DOCX.")
        nome_arquivo = filename or f"{self.project_data['titulo'].replace(' ', '_')}_Final.docx"
        
        conteudo_final = self.project_data.get("manuscrito_revisado") or self.project_data.get("manuscrito_original")
        
        path_final = self.exporter.gerar_ebook_docx(
            titulo=self.project_data["titulo"],
            autor=self.project_data["autor"],
            conteudo=conteudo_final,
            output_path=nome_arquivo,
            subtitulo=self.project_data["subtitulo"]
        )
        
        if path_final:
            logger.info(f"Processo concluído com sucesso. Arquivo: {path_final}")
            self.project_data["status"] = "CONCLUIDO_EXPORTADO"
        
        return path_final

# Autor: Renato Borges

if __name__ == "__main__":
    # Caminho do documento base para fundamentação pedagógica
    DOCUMENTO_BNCC = "EBOOK-FEQ-BNCC-DA-COMPUTACAO-Professorrenato-com.pdf"
    
    # Instanciação do Core
    app = EbookGenerator(DOCUMENTO_BNCC)
    
    # 1. Simulação da Tela 1: Upload de Manuscrito
    # Nota: Deve existir um arquivo 'manuscrito.docx' ou 'manuscrito.txt' para teste.
    if app.executar_tela_1_upload("Guia Prático BNCC 2026", "manuscrito.docx"):
        
        # 2. Simulação da Tela 2: Configurações de Design
        app.executar_tela_2_design(
            cores=["#1e3c72", "#2a5298"], 
            angulo=45, 
            autor="Prof. Renato Borges",
            subtitulo="Implementação do DC-GO Computação na Sala de Aula"
        )
        
        # 3. Simulação da Tela 3: Revisão de IA
        # O sistema busca no PDF termos sobre Eixos e Práticas Plugadas[cite: 112, 116, 117].
        sugestoes_painel = app.executar_tela_3_ia_revisao()
        print(sugestoes_painel)
        
        # 4. Exportação Final
        app.finalizar_e_exportar()
