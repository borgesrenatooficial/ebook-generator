"""
Nome do Script: ebook_generator.py
Autor: Renato Borges
Versão: 1.1.0
Propósito: Motor de diagramação profissional com suporte a rodapé dinâmico.
"""

import logging
from typing import List, Dict
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, ns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EbookEngine:
    def __init__(self, title: str):
        self.title = title
        self.doc = Document()
        self._setup_styles()

    def _setup_styles(self) -> None:
        """Configura padrões: H1=28pt, H2=22pt, Normal=16pt Justificado."""
        styles = self.doc.styles
        
        # Heading 1 (Arial 28 Bold)
        h1 = styles['Heading 1']
        h1.font.name, h1.font.size, h1.font.bold = 'Arial', Pt(28), True
        
        # Heading 2 (Arial 22 Bold)
        h2 = styles['Heading 2']
        h2.font.name, h2.font.size, h2.font.bold = 'Arial', Pt(22), True

        # Body (Calibri 16 Justified)
        n = styles['Normal']
        n.font.name, n.font.size = 'Calibri', Pt(16)
        n.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def _add_page_number(self, paragraph) -> None:
        """Insere campo PAGE do Word via XML nativo."""
        run = paragraph.add_run()
        fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(ns.qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText'); instrText.set(ns.qn('xml:space'), 'preserve'); instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(ns.qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar'); fldChar3.set(ns.qn('w:fldCharType'), 'end')
        run._r.extend([fldChar1, instrText, fldChar2, fldChar3])

    def build_ebook(self, content: List[Dict], output_path: str) -> None:
        """Executa a montagem do documento."""
        # Capa Centralizada
        cp = self.doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cp.add_run(f"\n\n\n{self.title}")
        run.font.size, run.font.bold = Pt(36), True
        self.doc.add_page_break()

        # Renderização do Conteúdo
        for block in content:
            t, txt = block.get("type"), block.get("text", "").strip()
            if not txt: continue
            if t == "h1": self.doc.add_heading(txt, level=1)
            elif t == "h2": self.doc.add_heading(txt, level=2)
            else: self.doc.add_paragraph(txt)

        # Rodapé com Numeração
        footer = self.doc.sections[0].footer
        self._add_page_number(footer.paragraphs[0])
        footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        self.doc.save(output_path)
        logger.info(f"Arquivo {output_path} gerado com sucesso.")
