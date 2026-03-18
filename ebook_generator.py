"""
Nome do Script: ebook_generator.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 1.1.0
Propósito: Engine de conversão e estilização de documentos .docx.
"""

import logging
from typing import List, Dict
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, ns

# Configuração de Log para monitoramento em produção (Railway)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EbookEngine:
    """Responsável pela padronização visual do eBook conforme briefing técnico."""

    def __init__(self, title: str):
        self.title = title
        self.doc = Document()
        self._apply_global_styles()

    def _apply_global_styles(self) -> None:
        """Define a tipografia: H1 (Arial 28), H2 (Arial 22), Body (Calibri 16)."""
        styles = self.doc.styles
        
        # Heading 1
        h1 = styles['Heading 1']
        h1.font.name, h1.font.size, h1.font.bold = 'Arial', Pt(28), True
        
        # Heading 2
        h2 = styles['Heading 2']
        h2.font.name, h2.font.size, h2.font.bold = 'Arial', Pt(22), True

        # Normal (Corpo do texto)
        normal = styles['Normal']
        normal.font.name, normal.font.size = 'Calibri', Pt(16)
        normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def _add_page_numbers(self) -> None:
        """Insere numeração de página no rodapé via manipulação de XML (OxmlElement)."""
        footer = self.doc.sections[0].footer
        paragraph = footer.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = paragraph.add_run()
        fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(ns.qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText'); instrText.set(ns.qn('xml:space'), 'preserve'); instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(ns.qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar'); fldChar3.set(ns.qn('w:fldCharType'), 'end')

        run._r.extend([fldChar1, instrText, fldChar2, fldChar3])

    def build(self, content: List[Dict], output_path: str) -> None:
        """Constrói o documento final: Capa -> Conteúdo -> Rodapé."""
        # Capa
        cp = self.doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cp.add_run(f"\n\n\n{self.title}")
        run.font.size, run.font.bold = Pt(36), True
        self.doc.add_page_break()

        # Corpo
        for item in content:
            style_type = item.get("type", "p")
            text = item.get("text", "").strip()
            if not text: continue

            if style_type == "h1":
                self.doc.add_heading(text, level=1)
            elif style_type == "h2":
                self.doc.add_heading(text, level=2)
            else:
                self.doc.add_paragraph(text)

        self._add_page_numbers()
        self.doc.save(output_path)
        logger.info(f"Sucesso: {output_path} gerado.")
