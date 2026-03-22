"""
Nome do Script: docx_export.py
Autor: Renato Borges
Data: 20 de Março de 2026
Versão: 2.0.0
Propósito: Exportação do conteúdo final revisado para o formato Microsoft Word (DOCX).
           Refatorado com foco rigoroso em Mobile-First (18pt) e layout BNCC.
"""

import logging
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Optional

# Configuração de Logging Profissional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DocxExporter")

class DocxExporter:
    """
    Especialista em converter o conteúdo processado pelo Ebook Generator
    em documentos Word formatados profissionalmente para leitura em smartphones.
    """

    def __init__(self):
        self.document = Document()

    def _configurar_estilos_padrao(self):
        """Configura fontes, tamanhos (18pt) e margens (Mobile-First) para o documento."""
        # Configuração de Largura Mobile
        section = self.document.sections[0]
        section.page_width = Cm(14.8)
        section.left_margin = section.right_margin = Cm(1.5)

        # Corpo do Texto - 18pt (Correção Crítica)
        style = self.document.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(18)
        style.paragraph_format.line_spacing = 1.5
        style.paragraph_format.space_after = Pt(12)

        # Título H1
        h1 = self.document.styles['Heading 1']
        h1.font.size = Pt(28)
        h1.font.bold = True
        h1.font.color.rgb = RGBColor(31, 56, 100) # Azul Profundo

    def gerar_ebook_docx(self, 
                         titulo: str, 
                         autor: str, 
                         conteudo: str, 
                         output_path: str = "ebook_final.docx",
                         subtitulo: Optional[str] = None) -> Optional[str]:
        """
        Cria o arquivo DOCX estruturado com capa (texto) e corpo do manuscrito.
        """
        try:
            logger.info(f"Iniciando exportação DOCX Mobile (18pt): {output_path}")
            self._configurar_estilos_padrao()

            # 1. Capa Simples no Início do Documento
            title_part = self.document.add_heading(titulo, level=1)
            title_part.alignment = WD_ALIGN_PARAGRAPH.CENTER

            if subtitulo:
                sub = self.document.add_paragraph(subtitulo)
                sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
                sub.runs[0].italic = True

            author_para = self.document.add_paragraph(f"\nAutor: {autor}")
            author_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            self.document.add_page_break()

            # 2. Inserção do Conteúdo
            paragrafos = conteudo.split('\n')
            for p in paragrafos:
                if p.strip():
                    if p.isupper() and len(p) < 100:
                        self.document.add_heading(p, level=1)
                    else:
                        para = self.document.add_paragraph(p)
                        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

            self.document.save(output_path)
            logger.info(f"✅ Arquivo DOCX gerado com sucesso em: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ Erro ao exportar DOCX: {e}")
            return None

# Autor: Renato Borges
