"""
Nome do Script: cover_generator.py
Autor: Renato Borges
Data: 20 de Março de 2026
Versão: 1.0.0
Propósito: Geração dinâmica de capas e contracapas com gradientes e textos.
           Reflete as configurações da Tela 2 do Ebook Generator.
"""

import logging
from PIL import Image, ImageDraw, ImageFont
import math
from typing import List, Tuple, Optional

# Configuração de Logging Profissional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CoverGenerator")

class CoverGenerator:
    """
    Especialista em criar capas de ebooks com design moderno.
    Suporta gradientes lineares, imagens de fundo e tipografia.
    """

    def __init__(self, width: int = 1600, height: int = 2400):
        """
        Define as dimensões padrão da capa (Proporção de ebook padrão).
        """
        self.width = width
        self.height = height
        self.font_path = "arial.ttf" # Deve estar disponível no ambiente

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Converte cores hexadecimais para tuplas RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def create_gradient_background(self, colors: List[str], angle: int) -> Image.Image:
        """
        Cria uma imagem com gradiente linear baseado no ângulo fornecido (Tela 2).
        """
        base = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(base)
        
        color1 = self._hex_to_rgb(colors[0])
        color2 = self._hex_to_rgb(colors[1])

        # Lógica matemática para aplicar o ângulo do gradiente
        angle_rad = math.radians(angle)
        for y in range(self.height):
            for x in range(self.width):
                # Projeção simplificada para o gradiente
                ratio = (x * math.cos(angle_rad) + y * math.sin(angle_rad)) / (self.width + self.height)
                ratio = max(0, min(1, ratio)) # Clamp entre 0 e 1
                
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                
                draw.point((x, y), fill=(r, g, b))
        
        return base

    def generate_cover(self, 
                       title: str, 
                       author: str, 
                       colors: List[str], 
                       angle: int,
                       subtitle: Optional[str] = None,
                       output_path: str = "capa_final.png"):
        """
        Orquestra a criação da capa completa: Fundo + Textos.
        """
        logger.info(f"Gerando capa para o título: {title}")
        
        # 1. Gerar Background
        image = self.create_gradient_background(colors, angle)
        draw = ImageDraw.Draw(image)

        # 2. Configurar Fontes (Tamanhos proporcionais)
        try:
            font_title = ImageFont.truetype(self.font_path, 160)
            font_sub = ImageFont.truetype(self.font_path, 80)
            font_author = ImageFont.truetype(self.font_path, 70)
        except IOError:
            logger.warning("Fonte não encontrada, usando fonte padrão.")
            font_title = font_sub = font_author = ImageFont.load_default()

        # 3. Desenhar Textos (Centralizados)
        # Título
        draw.text((self.width//2, self.height//3), title, font=font_title, fill="white", anchor="mm")
        
        # Subtítulo (se houver)
        if subtitle:
            draw.text((self.width//2, self.height//2), subtitle, font=font_sub, fill="white", anchor="mm")
            
        # Autor
        draw.text((self.width//2, self.height - 200), author, font=font_author, fill="white", anchor="mm")

        # 4. Salvar
        image.save(output_path)
        logger.info(f"Capa salva com sucesso em: {output_path}")
        return output_path

# Autor: Renato Borges
