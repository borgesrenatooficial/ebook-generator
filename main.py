"""
Nome do Script: main.py
Autor: Renato Borges
Data: 20 de Março de 2026
Version: 2.6.0
Propósito: Script principal de orquestração do Ebook Generator. 
           Integra Upload (Tela 1), Design (Tela 2) e Brain Processor (Tela 3).
"""

import logging
import os
from typing import Optional, Dict, Any

# Importação dos módulos especialistas (Devem estar na mesma pasta ou PYTHONPATH)
from manuscript_loader import ManuscriptProcessor
from brain_processor import BrainProcessor

# Configuração de Logging Profissional para monitoramento de automação
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("execution_log.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MainOrchestrator")

class EbookGenerator:
    """
    Classe principal que coordena a pipeline de criação do ebook.
    Especializada em automação de conteúdo para educação e tecnologia.
    """

    def __init__(self, pdf_context_path: str):
        """
        Inicializa os componentes do sistema.
        
        Args:
            pdf_context_path (str): Caminho do PDF BNCC/DC-GO para a base de conhecimento.
        """
        self.loader = ManuscriptProcessor()
        self.brain = BrainProcessor(pdf_context_path)
        self.current_project: Dict[str, Any] = {}
        logger.info("Sistema Ebook Generator inicializado com sucesso.")

    def iniciar_novo_projeto(self, nome_ebook: str, arquivo_path: str) -> bool:
        """
        Executa a lógica da Tela 1: Identificação e Ingestão de texto.
        Suporta apenas DOCX e TXT conforme especificado.
        """
        logger.info(f"Iniciando projeto: {nome_ebook}")
        
        # Extração do conteúdo bruto (Manuscrito)
        conteudo_bruto = self.loader.load(arquivo_path)
        
        if not conteudo_bruto:
            logger.error("Falha ao carregar o manuscrito. Verifique o arquivo.")
            return False

        self.current_project = {
            "nome": nome_ebook,
            "conteudo_original": conteudo_bruto,
            "path_origem": arquivo_path,
            "status": "TELA_1_CONCLUIDA"
        }
        
        logger.info(f"Conteúdo de {nome_ebook} carregado com sucesso.")
        return True

    def preparar_revisao_ia(self) -> str:
        """
        Executa a lógica da Tela 3: Aciona o cérebro para analisar o texto
        com base no PDF da BNCC de Computação.
        """
        if "conteudo_original" not in self.current_project:
            logger.error("Nenhum projeto ativo para revisão.")
            return "Erro: Projeto não inicializado."

        logger.info("Solicitando análise pedagógica ao BrainProcessor...")
        texto = self.current_project["conteudo_original"]
        
        # Gera sugestões baseadas no PDF (ex: Transversalidade, Eixos, Avaliação)
        sugestoes = self.brain.analyze_pedagogy(texto)
        
        # Retorna o texto formatado para o painel lateral da Tela 3
        return self.brain.format_for_display(sugestoes)

# Autor: Renato Borges

if __name__ == "__main__":
    # Exemplo de fluxo de execução simulando a interação do usuário
    # Caminho do seu PDF de referência anexado
    CAMINHO_PDF = "EBOOK-FEQ-BNCC-DA-COMPUTACAO-Professorrenato-com.pdf"
    
    app = EbookGenerator(CAMINHO_PDF)
    
    # Simulação: Usuário faz upload de um DOCX na Tela 1
    sucesso = app.iniciar_novo_projeto(
        nome_ebook="Manual de Computação Básica", 
        arquivo_path="manuscrito_teste.docx" # Arquivo de exemplo
    )
    
    if sucesso:
        # Simulação: Usuário clica em 'Revisão por IA' na Tela 3
        resultado_ia = app.preparar_revisao_ia()
        print(resultado_ia)
