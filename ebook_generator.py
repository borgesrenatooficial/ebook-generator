"""
Nome do Script: ebook_generator.py
Autor: Renato Borges
Versão: 2.2.2
Propósito: Diagramação Mobile-First (Fonte 18pt, Entrelinha 1.5).
"""

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement, ns

class EbookEngine:
    def __init__(self, title: str):
        self.title = title
        self.doc = Document()
        self._setup()

    def _setup(self):
        section = self.doc.sections[0]
        section.page_width = Cm(14.8) # Largura Mobile
        section.top_margin, section.bottom_margin = Cm(2.5), Cm(2.0)
        section.left_margin, section.right_margin = Cm(2.0), Cm(2.0)

        # Estilo Normal (Corpo do Texto)
        style = self.doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(18)
        style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        style.paragraph_format.space_after = Pt(12)

    def _add_page_number(self, paragraph):
        run = paragraph.add_run()
        fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(ns.qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText'); instrText.set(ns.qn('xml:space'), 'preserve'); instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(ns.qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar'); fldChar3.set(ns.qn('w:fldCharType'), 'end')
        run._r.extend([fldChar1, instrText, fldChar2, fldChar3])

    def build_ebook(self, content: list, output_path: str):
        """Método sincronizado com main.py"""
        # Capa
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"\n\n\n{self.title.upper()}")
        run.font.size, run.font.bold = Pt(32), True
        self.doc.add_page_break()

        for block in content:
            t, txt = block.get("type"), block.get("text", "")
            if t == "h1":
                self.doc.add_page_break()
                self.doc.add_heading(txt, level=1)
            elif t == "h2":
                self.doc.add_heading(txt, level=2)
            else:
                self.doc.add_paragraph(txt)

        footer = self.doc.sections[0].footer
        self._add_page_number(footer.paragraphs[0])
        self.doc.save(output_path)
