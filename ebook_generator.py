"""
Nome do Script: ebook_generator.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 2.0.0
Propósito: Engine de diagramação otimizada para leitura em dispositivos móveis.
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
    """Motor de diagramação focado em Leiturabilidade Mobile e normas ABNT."""

    def __init__(self, title: str):
        self.title = title
        self.doc = Document()
        self._configure_page_setup()
        self._apply_mobile_typography()

    def _configure_page_setup(self) -> None:
        """Configura margens conforme item 3 do briefing (Mobile Friendly)."""
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Cm(2.5)
            section.bottom_margin = Cm(2.0)
            section.left_margin = Cm(2.0)
            section.right_margin = Cm(2.0)
            # Define tamanho de página (A5 é excelente para simular celular no Word)
            section.page_height = Cm(21.0)
            section.page_width = Cm(14.8)

    def _apply_mobile_typography(self) -> None:
        """Aplica a hierarquia tipográfica do item 2 do briefing."""
        styles = self.doc.styles
        
        # H1 - Título de Capítulo (24pt)
        h1 = styles['Heading 1']
        h1.font.name, h1.font.size, h1.font.bold = 'Arial', Pt(24), True
        h1.paragraph_format.space_before = Pt(24)
        h1.paragraph_format.space_after = Pt(18)
        h1.paragraph_format.keep_with_next = True

        # H2 - Subtítulo de Seção (20pt)
        h2 = styles['Heading 2']
        h2.font.name, h2.font.size, h2.font.bold = 'Arial', Pt(20), True
        h2.paragraph_format.space_before = Pt(18)
        h2.paragraph_format.space_after = Pt(12)

        # H3 - Subseção (18pt)
        h3 = styles['Heading 3']
        h3.font.name, h3.font.size, h3.font.bold = 'Arial', Pt(18), True

        # Normal - Corpo do Texto (18pt para Celular)
        normal = styles['Normal']
        normal.font.name, normal.font.size = 'Arial', Pt(18)
        fmt = normal.paragraph_format
        fmt.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE # Entrelinha 1.5
        fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT # Alinhamento à esquerda (melhor p/ mobile)
        fmt.space_after = Pt(12) # Respiro entre parágrafos

    def _add_page_number(self, paragraph) -> None:
        """Numeração de página automática no rodapé."""
        run = paragraph.add_run()
        fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(ns.qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText'); instrText.set(ns.qn('xml:space'), 'preserve'); instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(ns.qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar'); fldChar3.set(ns.qn('w:fldCharType'), 'end')
        run._r.extend([fldChar1, instrText, fldChar2, fldChar3])

    def build(self, content: List[Dict], output_path: str) -> None:
        """Gera o Ebook seguindo a lógica de quebra de página e respiro."""
        # 1. Capa Mobile (Item 10)
        p_capa = self.doc.add_paragraph()
        p_capa.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_title = p_capa.add_run(f"\n\n\n{self.title.upper()}")
        run_title.font.size, run_title.font.bold = Pt(32), True
        
        p_author = self.doc.add_paragraph()
        p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_auth = p_author.add_run("\nEditora Digital: professorrenato.com")
        run_auth.font.size = Pt(14)
        
        self.doc.add_page_break()

        # 2. Sumário Simples (Placeholder para futura automação)
        self.doc.add_heading("SUMÁRIO", level=1)
        self.doc.add_paragraph("Os capítulos abaixo são gerados conforme seu arquivo.")
        self.doc.add_page_break()

        # 3. Processamento de Blocos
        for block in content:
            b_type = block.get("type", "p")
            text = block.get("text", "").strip()
            
            if not text: continue

            if b_type == "h1":
                # Quebra de página antes de cada H1 (Capítulo Novo)
                self.doc.add_page_break()
                self.doc.add_heading(text, level=1)
            elif b_type == "h2":
                self.doc.add_heading(text, level=2)
            elif b_type == "h3":
                self.doc.add_heading(text, level=3)
            else:
                self.doc.add_paragraph(text)

        # 4. Rodapé
        footer = self.doc.sections[0].footer
        para_foot = footer.paragraphs[0]
        para_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self._add_page_number(para_foot)

        self.doc.save(output_path)
        logger.info(f"Ebook mobile-ready gerado: {output_path}")
