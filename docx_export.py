"""
Nome do Script: docx_export.py
Autor: Renato Borges
Data: 20 de Março de 2026
Versão: 1.0.0
Propósito: Exportação do conteúdo final revisado para o formato Microsoft Word (DOCX).
"""

import logging
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Optional

# Configuração de Logging Profissional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DocxExporter")

class DocxExporter:
    """
    Especialista em converter o conteúdo processado pelo Ebook Generator
    em documentos Word formatados profissionalmente.
    """

    def __init__(self):
        self.document = Document()

    def _configurar_estilos_padrao(self):
        """Configura fontes e tamanhos padrão para o documento."""
        style = self.document.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(12)

    def gerar_ebook_docx(self, 
                         titulo: str, 
                         autor: str, 
                         conteudo: str, 
                         output_path: str = "ebook_final.docx",
                         subtitulo: Optional[str] = None):
        """
        Cria o arquivo DOCX estruturado com capa (texto) e corpo do manuscrito.
        """
        try:
            logger.info(f"Iniciando exportação DOCX: {output_path}")
            self._configurar_estilos_padrao()

            # 1. Capa Simples no Início do Documento
            title_part = self.document.add_heading(titulo, 0)
            title_part.alignment = WD_ALIGN_PARAGRAPH.CENTER

            if subtitulo:
                sub = self.document.add_paragraph(subtitulo)
                sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
                sub.runs[0].italic = True

            author_para = self.document.add_paragraph(f"\nAutor: {autor}")
            author_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            self.document.add_page_break()

            # 2. Inserção do Conteúdo (Manuscrito Revisado)
            # Dividimos o conteúdo por quebras de linha para manter parágrafos
            paragrafos = conteudo.split('\n')
            for p in paragrafos:
                if p.strip():
                    # Lógica simples: Se a linha for curta e em caixa alta, vira título
                    if p.isupper() and len(p) < 100:
                        self.document.add_heading(p, level=1)
                    else:
                        para = self.document.add_paragraph(p)
                        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

            # 3. Salvar Arquivo
            self.document.save(output_path)
            logger.info(f"Arquivo DOCX gerado com sucesso em: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erro ao exportar DOCX: {e}")
            return None

# Autor: Renato Borges
