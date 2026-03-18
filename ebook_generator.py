"""
Nome do Script: ebook_generator.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 2.2.0
Propósito: Engine de diagramação mobile com foco em hierarquia tipográfica e respiro visual.
"""

import logging
from typing import List, Dict
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement, ns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EbookEngine:
    def __init__(self, title: str):
        self.title = title
        self.doc = Document()
        self._configure_mobile_canvas()
        self._define_style_sheet()

    def _configure_mobile_canvas(self):
        """Ajusta o tamanho da página para simular a tela de um celular (Largura menor)."""
        section = self.doc.sections[0]
        # Margens conforme diretriz: 2.5 topo, 2.0 laterais/base [cite: 12]
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)
        # Tamanho A5 ou Executivo é melhor para leitura mobile
        section.page_width = Cm(14.8) 
        section.page_height = Cm(21.0)

    def _define_style_sheet(self):
        """Define a 'Folha de Estilos' conforme as especificações tipográficas."""
        styles = self.doc.styles

        # CORPO DO TEXTO (Normal) - Mínimo 18pt, Sem Serifa [cite: 4, 5]
        n = styles['Normal']
        n.font.name = 'Arial'
        n.font.size = Pt(18)
        n.font.color.rgb = RGBColor(30, 30, 30)
        fmt = n.paragraph_format
        fmt.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE # Entrelinha 1.5 [cite: 6]
        fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT # Melhor leitura no celular [cite: 6]
        fmt.space_after = Pt(18) # Área de respiro entre parágrafos [cite: 19]

        # H1 - Título Principal (24pt, Negrito) [cite: 7, 52]
        h1 = styles['Heading 1']
        h1.font.name = 'Arial'
        h1.font.size = Pt(24)
        h1.font.bold = True
        h1.font.color.rgb = RGBColor(0, 17, 46) # Azul Escuro (Sua paleta)
        h1.paragraph_format.space_before = Pt(30)
        h1.paragraph_format.space_after = Pt(20)

        # H2 - Subtítulo (20pt, Negrito) [cite: 8, 52]
        h2 = styles['Heading 2']
        h2.font.name = 'Arial'
        h2.font.size = Pt(20)
        h2.font.bold = True
        h2.paragraph_format.space_before = Pt(20)
        h2.paragraph_format.space_after = Pt(12)

        # H3 - Subseção (18pt, Negrito) [cite: 52]
        h3 = styles['Heading 3']
        h3.font.name = 'Arial'
        h3.font.size = Pt(18)
        h3.font.bold = True

    def _add_page_number(self, paragraph):
        """Insere numeração no rodapé [cite: 15]"""
        run = paragraph.add_run()
        fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(ns.qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText'); instrText.set(ns.qn('xml:space'), 'preserve'); instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(ns.qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar'); fldChar3.set(ns.qn('w:fldCharType'), 'end')
        run._r.extend([fldChar1, instrText, fldChar2, fldChar3])

    def build_ebook(self, content: List[Dict], output_path: str):
        # 1. CAPA PROFISSIONAL [cite: 41, 45]
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"\n\n\n\n{self.title.upper()}")
        run.font.size = Pt(32)
        run.font.bold = True
        
        p_sub = self.doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_sub = p_sub.add_run(f"\nEditora Digital: professorrenato.com") [cite: 47]
        run_sub.font.size = Pt(18)
        
        self.doc.add_page_break() [cite: 18]

        # 2. CONTEÚDO COM RESPIRO [cite: 22]
        for block in content:
            t, txt = block.get("type"), block.get("text", "").strip()
            if not txt: continue

            if t == "h1":
                self.doc.add_page_break() # Capítulos sempre em nova página [cite: 18]
                self.doc.add_heading(txt, level=1)
            elif t == "h2":
                self.doc.add_heading(txt, level=2)
            elif t == "h3":
                self.doc.add_heading(txt, level=3)
            else:
                # Quebra automática de parágrafos longos (Lógica de Mancha Gráfica) [cite: 14]
                para = self.doc.add_paragraph(txt)
                para.paragraph_format.keep_together = True # Evita parágrafo cortado [cite: 16]

        # 3. RODAPÉ [cite: 15]
        footer = self.doc.sections[0].footer
        self._add_page_number(footer.paragraphs[0])
        footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        self.doc.save(output_path)
        logger.info(f"Ebook formatado com sucesso: {output_path}")
