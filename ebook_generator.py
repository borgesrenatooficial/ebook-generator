"""
Nome do Script: ebook_generator.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 2.6.0 (Sênior - Edição BNCC)
Propósito: Solução definitiva para erro 502. Otimização de fluxo para Mobile-First.
"""

import logging
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement, ns

# Logging profissional para monitorar o progresso no servidor
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EbookEngine:
    def __init__(self, title: str):
        self.title = title
        self.doc = Document()
        self._configure_mobile_layout()

    def _configure_mobile_layout(self):
        """Aplica o layout Mobile-First (14.8cm) e estilos BNCC."""
        section = self.doc.sections[0]
        section.page_width = Cm(14.8)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = section.right_margin = Cm(1.5)

        # Estilo Normal (Corpo do Texto - 18pt)
        style = self.doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(18)
        style.paragraph_format.line_spacing = 1.5
        style.paragraph_format.space_after = Pt(12)

        # Estilo Heading 1 (Capítulos - 28pt)
        h1 = self.doc.styles['Heading 1']
        h1.font.size = Pt(28)
        h1.font.bold = True
        h1.font.color.rgb = RGBColor(31, 56, 100) # Azul BNCC

        # Estilo Heading 2 (Perguntas/Subtítulos - 22pt)
        h2 = self.doc.styles['Heading 2']
        h2.font.size = Pt(22)
        h2.font.bold = True
        h2.font.color.rgb = RGBColor(64, 64, 64) # Cinza Grafite

    def _insert_page_number(self):
        """Adiciona numeração de página centralizada de forma leve."""
        footer = self.doc.sections[0].footer
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        
        # Inserção de campo XML 'PAGE'
        fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(ns.qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText'); instrText.set(ns.qn('xml:space'), 'preserve'); instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(ns.qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar'); fldChar3.set(ns.qn('w:fldCharType'), 'end')
        run._r.extend([fldChar1, instrText, fldChar2, fldChar3])

    def build_ebook(self, content: list, output_path: str):
        """
        Gera o documento final. Compatível com a chamada do main.py.
        :param content: Lista de dicts [{'type': 'h1', 'text': '...'}, ...]
        """
        try:
            logging.info(f"Iniciando build do eBook: {self.title}")
            
            # Capa Profissional
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(f"\n\n\n{self.title.upper()}")
            run.font.size, run.bold = Pt(32), True
            self.doc.add_page_break()

            # Processamento do conteúdo BNCC [cite: 1, 7, 15]
            for block in content:
                t, txt = block.get("type"), block.get("text", "")
                if t == "h1":
                    self.doc.add_heading(txt, level=1)
                elif t == "h2":
                    self.doc.add_heading(txt, level=2)
                else:
                    self.doc.add_paragraph(txt)

            self._insert_page_number()
            self.doc.save(output_path)
            logging.info(f"✅ Arquivo salvo em: {output_path}")

        except Exception as e:
            logging.error(f"❌ Erro crítico no servidor: {e}")
            raise e
