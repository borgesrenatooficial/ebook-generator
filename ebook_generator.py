"""
Nome do Script: ebook_generator_bncc.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 2.3.0
Propósito: Diagramação de alto padrão para o Ebook BNCC da Computação.
           Foco em legibilidade (18pt) e hierarquia visual (H1 28, H2 22).
"""

import logging
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement, ns

# Configuração de Logging para auditoria de processos
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EbookEngine:
    def __init__(self, title: str):
        """
        Inicializa o documento com o título fornecido.
        :param title: Título principal do eBook.
        """
        self.title = title
        self.doc = Document()
        self._setup_styles()
        logging.info(f"Engine iniciada para: {self.title}")

    def _setup_styles(self):
        """
        Configura a tipografia e o layout da página seguindo a teoria das cores.
        """
        section = self.doc.sections[0]
        # Layout Mobile-Friendly (A5 aproximado para leitura digital)
        section.page_width = Cm(15.0)
        section.left_margin = section.right_margin = Cm(2.0)
        
        # Estilo Normal (Corpo do Texto) - 18pt [Diretriz do Usuário]
        style = self.doc.styles['Normal']
        style.font.name = 'Calibri'
        style.font.size = Pt(18)
        style.paragraph_format.line_spacing = 1.5
        style.paragraph_format.space_after = Pt(14)
        
        # Heading 1 (Capítulos) - 28pt
        h1 = self.doc.styles['Heading 1']
        h1.font.name = 'Arial'
        h1.font.size = Pt(28)
        h1.font.bold = True
        h1.font.color.rgb = RGBColor(31, 56, 100) # Azul Profundo BNCC
        
        # Heading 2 (Subtítulos/Questões) - 22pt
        h2 = self.doc.styles['Heading 2']
        h2.font.name = 'Arial'
        h2.font.size = Pt(22)
        h2.font.bold = True
        h2.font.color.rgb = RGBColor(64, 64, 64) # Cinza Grafite

    def _add_page_number(self, paragraph):
        """
        Insere o código XML para numeração dinâmica de páginas.
        """
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run()
        
        def make_element(name):
            return OxmlElement(name)

        fldChar1 = make_element('w:fldChar'); fldChar1.set(ns.qn('w:fldCharType'), 'begin')
        instrText = make_element('w:instrText'); instrText.set(ns.qn('xml:space'), 'preserve'); instrText.text = "PAGE"
        fldChar2 = make_element('w:fldChar'); fldChar2.set(ns.qn('w:fldCharType'), 'separate')
        fldChar3 = make_element('w:fldChar'); fldChar3.set(ns.qn('w:fldCharType'), 'end')
        
        run._r.extend([fldChar1, instrText, fldChar2, fldChar3])

    def generate(self, content: list, filename: str):
        """
        Executa a construção do eBook baseada em blocos de conteúdo.
        """
        try:
            # Capa Profissional
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(f"\n\n\n{self.title.upper()}\n")
            run.font.size, run.bold = Pt(32), True
            self.doc.add_page_break()

            # Processamento de Blocos [cite: 36, 40, 53]
            for block in content:
                type_ = block.get("type")
                text = block.get("text", "")
                
                if type_ == "h1":
                    self.doc.add_heading(text, level=1)
                elif type_ == "h2":
                    self.doc.add_heading(text, level=2)
                else:
                    para = self.doc.add_paragraph(text)
                    para.alignment = WD_ALIGN_PARAGRAPH.BOTH
                
                if block.get("break"):
                    self.doc.add_page_break()

            # Rodapé com Página
            self._add_page_number(self.doc.sections[0].footer.paragraphs[0])
            
            self.doc.save(filename)
            logging.info(f"Arquivo {filename} gerado com sucesso.")
        except Exception as e:
            logging.error(f"Erro na geração: {e}")

if __name__ == "__main__":
    # Conteúdo estruturado a partir do Documento Base [cite: 7, 34, 111]
    ebook_data = [
        {"type": "h1", "text": "INTRODUÇÃO", "break": False},
        {"type": "p", "text": "A inserção da Computação na Educação Básica é uma das maiores inovações curriculares do nosso tempo. [cite: 29]"},
        {"type": "h1", "text": "CAPÍTULO 1", "break": False},
        {"type": "h2", "text": "Implementação na Escola e no PPP", "break": False},
        {"type": "p", "text": "A escola não precisa criar uma disciplina nova. A orientação é trabalhar de forma transversal. [cite: 36, 38]"},
        {"type": "h1", "text": "CONCLUSÃO", "break": False},
        {"type": "p", "text": "O objetivo é preparar os alunos para pensarem de forma estruturada e ética. [cite: 113, 114]"}
    ]

    # Execução
    app = EbookEngine("BNCC DA COMPUTAÇÃO")
    app.generate(ebook_data, "Ebook_BNCC_Final_V2.3.docx")
