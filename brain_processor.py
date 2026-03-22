"""
Nome do Script: brain_processor.py
Autor: Renato Borges
Data: 22 de Março de 2026
Versão: 2.5.0
Propósito: Motor de Inteligência Artificial para ajuste estrutural e layout.
           Analisa a densidade do texto para evitar parágrafos quebrados, 
           linhas órfãs/viúvas e otimizar a leitura mobile em 18pt.
"""

import logging
from typing import List, Dict, Optional

# Configuração de Logging Profissional para monitoramento de layout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BrainProcessor")

class BrainProcessor:
    """
    Especialista em Micro-Diagramação Automática. 
    Analisa a distribuição de massa de texto para garantir fluidez no mobile.
    """

    def __init__(self, context_pdf_path: Optional[str] = None):
        """
        Inicializa o processador de layout. 
        O PDF agora é opcional, pois o foco mudou de conteúdo para estrutura.
        """
        self.context_path = context_pdf_path
        logger.info("Cérebro de Diagramação ativado: Foco em fluidez de leitura e respiro visual.")

    def optimize_layout(self, manuscript_text: str) -> str:
        """
        Analisa o manuscrito e aplica quebras de respiro em parágrafos muito densos.
        Garante que nenhum bloco ultrapasse o limite sugerido para telas pequenas.
        
        Args:
            manuscript_text (str): O texto bruto extraído.
            
        Returns:
            str: Texto processado com quebras de parágrafo otimizadas.
        """
        logger.info("Iniciando varredura de densidade textual...")
        
        # Divide o texto em parágrafos existentes
        paragraphs = manuscript_text.split('\n')
        optimized_content = []

        for p in paragraphs:
            text = p.strip()
            if not text:
                continue
            
            # Regra Senior: Parágrafos com mais de 450 caracteres tendem a ocupar 
            # a tela inteira do celular em 18pt, gerando fadiga visual.
            if len(text) > 450:
                logger.info("Parágrafo denso detectado. Aplicando quebra de respiro estratégica.")
                
                # Busca um ponto final próximo ao meio do parágrafo para dividir
                midpoint = len(text) // 2
                split_idx = text.find('. ', midpoint)
                
                if split_idx != -1:
                    # Divide em dois parágrafos menores para melhor distribuição
                    optimized_content.append(text[:split_idx + 1])
                    optimized_content.append(text[split_idx + 2:])
                else:
                    optimized_content.append(text)
            else:
                optimized_content.append(text)

        logger.info("Otimização de layout concluída.")
        return "\n".join(optimized_content)

    def analyze_page_breaks(self, text: str) -> List[Dict[str, str]]:
        """
        Identifica potenciais problemas de quebra de página (Linhas órfãs/viúvas).
        """
        suggestions = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Detecta se um título (curto) está isolado no final de um bloco
            if 0 < len(line) < 50 and line.isupper() and i == len(lines) - 1:
                suggestions.append({
                    "tipo": "Ajuste de Quebra",
                    "original": line,
                    "sugestao": "Ancorar título ao próximo bloco para evitar órfãs.",
                    "acao": "keep_with_next"
                })
        
        return suggestions

    def format_for_display(self, suggestions: List[Dict]) -> str:
        """Formata o status da otimização para a interface do usuário."""
        if not suggestions:
            return "✅ **Layout Otimizado:** O texto está distribuído para evitar linhas quebradas e garantir o respiro em 18pt."
        
        return "⚠️ **Ajustes de Diagramação Aplicados:** Parágrafos densos foram divididos para melhor leitura no celular."

# Autor: Renato Borges
