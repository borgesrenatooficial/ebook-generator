"""
Nome do Script: ebook_generator.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 1.0.0
Propósito: Automatizar a criação de eBooks em formato .docx com formatação 
           profissional, controle de estilos (H1, H2, Body) e paginação.
"""

import logging
from typing import List, Dict, Any
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Configuração de Logging para monitoramento profissional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EbookEngine:
    """
    Classe responsável pela lógica de construção e diagramação do eBook.
    """

    def __init__(self, title: str):
        """
        Inicializa o documento e define as configurações base.
        :param title: Título principal do eBook.
        """
        self.doc = Document()
        self.title = title
        logging.info(f"Iniciando criação do eBook: {self.title}")

    def _set_font_style(self, style_obj, font_name: str, size: int, bold: bool = False):
        """
        Helper para configurar propriedades de fonte de forma consistente.
        """
        font = style_obj.font
        font.name = font_name
        font.size = Pt(size)
        font.bold = bold
        # Necessário para garantir que a fonte seja aplicada corretamente no Word
        r_fonts = style_obj.element.rPr.get_or_add_rFonts()
        r_fonts.set(qn('w:eastAsia'), font_name)

    def configure_styles(self):
        """
        Configura os estilos globais de H1, H2 e Corpo de texto conforme solicitado.
        """
        # Estilo Título (H1) - 28pt
        h1 = self.doc.styles['Heading 1']
        self._set_font_style(h1, 'Arial', 28, True)
        
        # Estilo Subtítulo (H2) - 22pt
        h2 = self.doc.styles['Heading 2']
        self._set_font_style(h2, 'Arial', 22, True)
        
        # Estilo Normal (Corpo) - 16pt (ou 18pt conforme sua preferência)
        normal = self.doc.styles['Normal']
        self._set_font_style(normal, 'Calibri', 16, False)
        
        logging.info("Estilos de tipografia configurados com sucesso.")

    def add_page_number(self):
        """
        Adiciona numeração de página no rodapé (Lógica XML para python-docx).
        """
        footer = self.doc.sections[0].footer
        paragraph = footer.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = paragraph.add_run()
        
        def create_element(name):
            return OxmlElement(name)

        def create_attribute(element, name, value):
            element.set(qn(name), value)

        fldChar1 = create_element('w:fldChar')
        create_attribute(fldChar1, 'w:fldCharType', 'begin')
        
        instrText = create_element('w:instrText')
        create_attribute(instrText, 'xml:space', 'preserve')
        instrText.text = "PAGE"
        
        fldChar2 = create_element('w:fldChar')
        create_attribute(fldChar2, 'w:fldCharType', 'end')
        
        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)

    def build_ebook(self, content: List[Dict[str, Any]], filename: str):
        """
        Executa a montagem do documento seguindo a estrutura modular.
        :param content: Lista de dicionários contendo 'type' (h1, h2, p) e 'text'.
        :param filename: Nome do arquivo de saída.
        """
        try:
            self.configure_styles()
            
            # Capa Simples
            title_page = self.doc.add_heading(self.title, 0)
            title_page.alignment = WD_ALIGN_PARAGRAPH.CENTER
            self.doc.add_page_break()

            # Processamento de Conteúdo
            for item in content:
                if item['type'] == 'h1':
                    self.doc.add_heading(item['text'], level=1)
                elif item['type'] == 'h2':
                    self.doc.add_heading(item['text'], level=2)
                elif item['type'] == 'p':
                    p = self.doc.add_paragraph(item['text'])
                    p.alignment = WD_ALIGN_PARAGRAPH.BOTH
                
                # Opcional: Evitar quebras de página entre títulos e parágrafos seguintes
                if item.get('break_page'):
                    self.doc.add_page_break()

            self.add_page_number()
            self.doc.save(filename)
            logging.info(f"EBook gerado com sucesso: {filename}")
            
        except Exception as e:
            logging.error(f"Erro ao gerar eBook: {e}")

if __name__ == "__main__":
    # Exemplo de uso do motor de diagramação
    # Aqui você deve inserir seus textos soltos organizados por tipo
    meu_conteudo = [
        {"type": "h1", "text": "Introdução ao Mercado Spot", "break_page": False},
        {"type": "p", "text": "Neste capítulo, exploraremos a base das corretoras de cripto..."},
        {"type": "h2", "text": "Estratégia de Grid Trading", "break_page": False},
        {"type": "p", "text": "O Grid Trading é uma ferramenta poderosa para mercados laterais..."},
    ]

    engine = EbookEngine("Guia Mestre de Automação Crypto")
    engine.build_ebook(meu_conteudo, "Ebook_RenatoBorges_V1.docx")
