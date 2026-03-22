# Ebook Generator Pro 🚀

API Sênior para automação e geração de eBooks profissionais em `.docx`.

## 📌 Diretrizes do Projeto
* **Mobile-First Rigoroso:** Otimizado para leitura em smartphones sem zoom.
* **Tipografia:** Estilos H1 (Arial 28pt, Azul BNCC), H2 (22pt), e Corpo do Texto (Arial **18pt**). Entrelinha de 1.5.
* **Inteligência Pedagógica:** Revisão transversal focada no Documento Curricular para Goiás (DC-GO) e BNCC Computação.
* **Deploy:** Otimizado para Railway (`uvicorn api_handler:app`).

## ⚙️ Como usar (Endpoint da API)
O sistema aceita envios em Multipart/Form-Data através do endpoint:
`POST /process-full-ebook/`

**Parâmetros Esperados:**
* `file`: Arquivo `.docx` ou `.txt`
* `title`: Título da obra
* `author`: Nome do autor
* `color1` / `color2` / `angle`: Definições do gradiente da capa.

---
**Autor:** Renato Borges | professorrenato.com
