"""
Nome do Script: ebook_generator.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 2.1.0
Propósito: Motor de diagramação otimizado para Mobile (Mobile-First).
"""

import logging
from typing import List, Dict
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement, ns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EbookEngine:
    def __init__(self, title: str):
        self.title = title
        self.doc = Document()
        self._setup_margins()
        self._apply_mobile_styles()

    def _setup_margins(self):
        """Margens de 2cm conforme as novas orientações de diagramação."""
        for section in self.doc.sections:
            section.top_margin = Cm(2.5)
            section.bottom_margin = Cm(2.0)
            section.left_margin = Cm(2.0)
            section.right_margin = Cm(2.0)

    def _apply_mobile_styles(self):
        """Hierarquia Mobile: H1=24pt, H2=20pt, Corpo=18pt."""
        styles = self.doc.styles
        
        # Heading 1 (Capítulos)
        h1 = styles['Heading 1']
        h1.font.name, h1.font.size, h1.font.bold = 'Arial', Pt(24), True
        
        # Heading 2 (Subtítulos)
        h2 = styles['Heading 2']
        h2.font.name, h2.font.size, h2.font.bold = 'Arial', Pt(20), True

        # Normal (Corpo do texto - 18pt para Celular)
        n = styles['Normal']
        n.font.name, n.font.size = 'Arial', Pt(18)
        n.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        n.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT # Mobile prefere alinhado à esquerda
        n.paragraph_format.space_after = Pt(12)

    def _add_page_number(self, paragraph):
        """Campo XML para numeração automática."""
        run = paragraph.add_run()
        fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(ns.qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText'); instrText.set(ns.qn('xml:space'), 'preserve'); instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(ns.qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar'); fldChar3.set(ns.qn('w:fldCharType'), 'end')
        run._r.extend([fldChar1, instrText, fldChar2, fldChar3])

    def build_ebook(self, content: List[Dict], output_path: str):
        """
        NOME DO MÉTODO SINCRONIZADO COM MAIN.PY
        """
        # Capa
        cp = self.doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cp.add_run(f"\n\n\n{self.title.upper()}")
        run.font.size, run.font.bold = Pt(32), True
        self.doc.add_page_break()

        # Conteúdo
        for block in content:
            t, txt = block.get("type"), block.get("text", "").strip()
            if not txt: continue
            if t == "h1": 
                self.doc.add_page_break()
                self.doc.add_heading(txt, level=1)
            elif t == "h2": self.doc.add_heading(txt, level=2)
            else: self.doc.add_paragraph(txt)

        # Rodapé
        footer = self.doc.sections[0].footer
        self._add_page_number(footer.paragraphs[0])
        footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        self.doc.save(output_path)
        logger.info(f"Ebook '{output_path}' gerado com sucesso.")
