"""
Nome do Script: manuscript_loader.py
Autor: Renato Borges
Data: 22 de Março de 2026
Versão: 2.0.0
Propósito: Módulo de ingestão de dados. Extrai e limpa textos de manuscritos
           nos formatos DOCX e TXT para alimentar a esteira de produção do Ebook.
"""

import os
import logging
from typing import Optional
from docx import Document

# Configuração de Logging Padrão Sênior para auditoria e monitoramento
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ManuscriptLoader")

class ManuscriptProcessor:
    """
    Classe especialista em processamento de inputs (Manuscritos brutos).
    Garante que o texto chegue limpo e íntegro para a análise da Inteligência Artificial.
    """

    def __init__(self):
        # Extensões homologadas e seguras para a plataforma
        self.supported_extensions = [".docx", ".txt"]

    def load(self, file_path: str) -> Optional[str]:
        """
        Orquestra o carregamento do arquivo com base na sua extensão.
        
        Args:
            file_path (str): Caminho absoluto ou relativo do arquivo recebido da API.
        
        Returns:
            Optional[str]: O texto extraído em formato string, ou None em caso de falha crítica.
        """
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado no sistema: {file_path}")
            return None

        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.supported_extensions:
            logger.error(f"Formato não suportado: {ext}. Apenas arquivos {self.supported_extensions} são aceitos.")
            return None

        logger.info(f"Iniciando extração do arquivo: {os.path.basename(file_path)}")
        
        if ext == ".docx":
            return self._process_docx(file_path)
        return self._process_txt(file_path)

    def _process_docx(self, path: str) -> str:
        """
        Extrai o texto de arquivos Word preservando rigorosamente a estrutura de parágrafos.
        """
        try:
            doc = Document(path)
            # Unindo os parágrafos com quebra de linha (\n) para manter a blocagem original do autor
            content = "\n".join([para.text for para in doc.paragraphs])
            logger.info("Extração de DOCX concluída com sucesso.")
            return content
        except Exception as e:
            logger.error(f"Falha ao realizar parse do DOCX: {e}")
            return ""

    def _process_txt(self, path: str) -> str:
        """
        Lê arquivos TXT implementando fallback de encoding (UTF-8 -> Latin-1)
        para evitar crash (Erro 500) em arquivos originários de sistemas Windows mais antigos.
        """
        try:
            try:
                # Tenta leitura padrão web (UTF-8)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Fallback de segurança para ISO-8859-1 se o UTF-8 falhar
                logger.warning("Falha de encoding UTF-8. Acionando fallback de segurança para Latin-1.")
                with open(path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            logger.info("Extração de TXT concluída com sucesso.")
            return content
        except Exception as e:
            logger.error(f"Falha crítica na leitura do TXT: {e}")
            return ""

# Autor: Renato Borges
