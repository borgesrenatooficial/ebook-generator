"""
Nome do Script: main.py
Autor: Renato Borges
Data: 18 de Março de 2026
Versão: 1.2.0
Propósito: API FastAPI com suporte opcional à revisão via IA (Perplexity/OpenAI).
"""

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import os, uuid, logging, httpx
from ebook_generator import EbookEngine

# --- CONFIGURAÇÕES INICIAIS ---
app = FastAPI()
logger = logging.getLogger("uvicorn")

# Chave de API via Variável de Ambiente (Mais seguro)
# No Railway, adicione em 'Variables' o nome: PERPLEXITY_API_KEY
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "") 

async def review_text_with_ai(text: str) -> str:
    """
    Envia o texto para a Perplexity para otimização mobile-first.
    Se não houver chave ou houver erro, retorna o texto original.
    """
    if not PERPLEXITY_API_KEY:
        logger.warning("IA Skip: PERPLEXITY_API_KEY não configurada.")
        return text

    logger.info("Iniciando revisão via IA...")
    
    # Prompt focado nas diretrizes de diagramação mobile
    prompt = (
        "Você é um editor sênior de eBooks. Reescreva o texto a seguir focando em leitura em celular: "
        "1. Mantenha as marcações # para H1 e ## para H2. "
        "2. Quebre parágrafos longos em blocos de no máximo 4 linhas. "
        "3. Melhore a clareza e ortografia sem alterar o significado técnico. "
        "Texto:\n\n" + text
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "pplx-7b-online", # Ou o modelo de sua preferência
                    "messages": [
                        {"role": "system", "content": "Você é um assistente especializado em edição de texto."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Erro na API Perplexity: {response.text}")
                return text
    except Exception as e:
        logger.error(f"Falha na comunicação com IA: {e}")
        return text

def cleanup(files: list):
    """Remove arquivos temporários do servidor para economizar storage."""
    for f in files:
        if os.path.exists(f): 
            os.remove(f)
            logger.info(f"Removido: {f}")

def parse_txt_safe(content_bytes: bytes) -> list:
    """Decodifica binário e extrai estrutura de cabeçalhos."""
    try:
        text = content_bytes.decode('utf-8')
    except UnicodeDecodeError:
        text = content_bytes.decode('latin-1')
    
    parsed = []
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith("# "): parsed.append({"type": "h1", "text": line[2:]})
        elif line.startswith("## "): parsed.append({"type": "h2", "text": line[3:]})
        else: parsed.append({"type": "p", "text": line})
    return parsed

@app.post("/upload-ebook/")
async def upload_ebook(
    bg: BackgroundTasks,
    title: str = Form(...),
    filename: str = Form("ebook.docx"),
    file: UploadFile = File(...)
):
    uid = str(uuid.uuid4())
    in_file = f"in_{uid}_{file.filename}"
    out_file = f"out_{uid}.docx"

    try:
        # 1. Salva o arquivo temporário
        content = await file.read()
        with open(in_file, "wb") as f: f.write(content)

        # 2. Processamento de Texto
        if file.filename.endswith('.txt'):
            raw_text = content.decode('utf-8', errors='replace')
            
            # --- INTEGRAÇÃO COM IA ---
            # O texto passa pela revisão antes de virar a lista de objetos
            reviewed_text = await review_text_with_ai(raw_text)
            data = parse_txt_safe(reviewed_text.encode('utf-8'))
            # -------------------------
        else:
            # Para DOCX, extraímos os parágrafos mantendo lógica simples
            from docx import Document as DocxReader
            doc = DocxReader(in_file)
            data = [{"type": "p", "text": p.text} for p in doc.paragraphs if p.text.strip()]

        # 3. Geração do Documento via EbookEngine
        engine = EbookEngine(title)
        engine.build_ebook(data, out_file)

        # 4. Stream de retorno e limpeza
        file_handle = open(out_file, mode="rb")
        bg.add_task(cleanup, [in_file, out_file])

        return StreamingResponse(
            file_handle,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        cleanup([in_file, out_file])
        logger.error(f"Erro Crítico na Geração: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no processamento do Ebook.")

@app.get("/")
def health(): 
    return {
        "status": "online", 
        "ia_enabled": bool(PERPLEXITY_API_KEY),
        "engine_version": "2.0.0-MobileReady"
    }
