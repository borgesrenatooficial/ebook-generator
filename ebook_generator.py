"""
Nome do Script: ebook_engine.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 1.0.0
Propósito: Motor de processamento e formatação de documentos .docx (EbookEngine).
"""

import logging
from typing import List, Dict
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, ns

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EbookEngine:
    """Classe responsável pela lógica de estilização e geração do arquivo .docx."""

    def __init__(self, title: str):
        """
        Inicializa o motor com o título do eBook.
        
        :param title: Título principal que aparecerá na capa.
        """
        self.title = title
        self.doc = Document()
        self._setup_styles()

    def _setup_styles(self) -> None:
        """Configura os estilos globais (H1, H2, Normal) conforme briefing técnico."""
        try:
            # Heading 1 -> Arial 28pt Bold
            h1 = self.doc.styles['Heading 1']
            h1.font.name = 'Arial'
            h1.font.size = Pt(28)
            h1.font.bold = True

            # Heading 2 -> Arial 22pt Bold
            h2 = self.doc.styles['Heading 2']
            h2.font.name = 'Arial'
            h2.font.size = Pt(22)
            h2.font.bold = True

            # Normal -> Calibri 16pt Justificado
            normal = self.doc.styles['Normal']
            normal.font.name = 'Calibri'
            normal.font.size = Pt(16)
            normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            logger.info("Estilos tipográficos configurados com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao configurar estilos: {e}")

    def _add_page_number(self, run) -> None:
        """
        Insere o campo XML de numeração de página automática (PAGE).
        """
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(ns.qn('w:fldCharType'), 'begin')

        instrText = OxmlElement('w:instrText')
        instrText.set(ns.qn('xml:space'), 'preserve')
        instrText.text = "PAGE"

        fldChar2 = OxmlElement('w:fldChar')
        h = ns.qn('w:fldCharType')
        fldChar2.set(h, 'separate')

        fldChar3 = OxmlElement('w:fldChar')
        fldChar3.set(ns.qn('w:fldCharType'), 'end')

        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)
        run._r.append(fldChar3)

    def build_ebook(self, content: List[Dict[str, str]], filename: str) -> None:
        """
        Gera o documento final baseado na lista de blocos de conteúdo.
        
        :param content: Lista de dicts contendo {'type': 'h1'|'h2'|'p', 'text': '...'}
        :param filename: Nome do arquivo de saída.
        """
        # 1. Capa
        para_title = self.doc.add_paragraph()
        para_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para_title.add_run(self.title)
        run.font.size = Pt(36)
        run.font.bold = True
        
        self.doc.add_page_break()

        # 2. Processamento do Conteúdo
        for block in content:
            text_type = block.get("type")
            text_val = block.get("text", "").strip()

            if not text_val:
                continue

            if text_type == "h1":
                self.doc.add_heading(text_val, level=1)
            elif text_type == "h2":
                self.doc.add_heading(text_val, level=2)
            else:
                self.doc.add_paragraph(text_val)

        # 3. Rodapé com Numeração
        footer = self.doc.sections[0].footer
        para_footer = footer.paragraphs[0]
        para_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self._add_page_number(para_footer.add_run())

        self.doc.save(filename)
        logger.info(f"Ebook '{filename}' gerado com sucesso.")
