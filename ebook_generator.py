"""
Nome do Script: ebook_architect_bncc.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 2.4.0
Propósito: Diagramação profissional de eBook .docx com foco em BNCC Computação.
           Configurações: H1 (28pt), H2 (22pt), Corpo (18pt), Mobile-First.
"""

import logging
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement, ns

# Setup de Logging para monitoramento de execução
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EbookGenerator:
    def __init__(self, title: str):
        self.doc = Document()
        self.title = title
        self._apply_master_settings()

    def _apply_master_settings(self):
        """Define o setup de página e estilos globais."""
        section = self.doc.sections[0]
        # Largura otimizada para leitura em dispositivos móveis (Mobile-First)
        section.page_width = Cm(14.8)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)

        # Configuração Estilo Normal (Corpo do Texto - 18pt)
        style_n = self.doc.styles['Normal']
        style_n.font.name = 'Calibri'
        style_n.font.size = Pt(18)
        style_n.paragraph_format.line_spacing = 1.5
        style_n.paragraph_format.space_after = Pt(12)
        style_n.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.BOTH

        # Configuração Heading 1 (Capítulos - 28pt)
        style_h1 = self.doc.styles['Heading 1']
        style_h1.font.name = 'Arial'
        style_h1.font.size = Pt(28)
        style_h1.font.bold = True
        style_h1.font.color.rgb = RGBColor(31, 56, 100) # Azul Escuro

        # Configuração Heading 2 (Subtítulos - 22pt)
        style_h2 = self.doc.styles['Heading 2']
        style_h2.font.name = 'Arial'
        style_h2.font.size = Pt(22)
        style_h2.font.bold = True
        style_h2.font.color.rgb = RGBColor(64, 64, 64) # Cinza Grafite

    def add_page_number(self, paragraph):
        """Insere numeração de página automática no centro do rodapé."""
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run()
        
        fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(ns.qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText'); instrText.set(ns.qn('xml:space'), 'preserve'); instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(ns.qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar'); fldChar3.set(ns.qn('w:fldCharType'), 'end')
        
        run._r.extend([fldChar1, instrText, fldChar2, fldChar3])

    def create_ebook(self, content_list: list, filename: str):
        """Monta o documento com base na lista de blocos."""
        try:
            # Capa
            capa = self.doc.add_paragraph()
            capa.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_capa = capa.add_run(f"\n\n\n{self.title.upper()}")
            run_capa.font.size, run_capa.bold = Pt(32), True
            self.doc.add_page_break()

            # Processamento Dinâmico
            for block in content_list:
                tag = block.get("type")
                txt = block.get("text", "")

                if tag == "h1":
                    self.doc.add_heading(txt, level=1)
                elif tag == "h2":
                    self.doc.add_heading(txt, level=2)
                else:
                    self.doc.add_paragraph(txt)

            # Rodapé
            footer = self.doc.sections[0].footer
            self.add_page_number(footer.paragraphs[0])

            self.doc.save(filename)
            logging.info(f"✅ Ebook '{filename}' gerado com sucesso!")
        except Exception as e:
            logging.error(f"❌ Falha crítica: {e}")

if __name__ == "__main__":
    # Conteúdo estruturado conforme o Documento Base [cite: 7, 35, 52]
    data = [
        {"type": "h1", "text": "INTRODUÇÃO"},
        {"type": "p", "text": "A inserção da Computação na Educação Básica é uma das maiores inovações curriculares do nosso tempo. [cite: 29]"},
        {"type": "h1", "text": "CAPÍTULO 1: IMPLEMENTAÇÃO"},
        {"type": "h2", "text": "A escola precisa de uma disciplina nova?"},
        {"type": "p", "text": "Não. A orientação para a RME-Goiânia é a abordagem transversal, integrando habilidades aos componentes já existentes. "},
        {"type": "h1", "text": "CONCLUSÃO"},
        {"type": "p", "text": "O futuro constrói-se na sua sala de aula! [cite: 116]"}
    ]

    # Instanciação e Execução
    engineer = EbookGenerator("BNCC DA COMPUTAÇÃO")
    engineer.create_ebook(data, "Ebook_BNCC_Computacao_RenatoBorges.docx")
