<?php
/**
 * Plugin Name: Ebook Generator Professional
 * Description: Automação 360° para eBooks DOCX (Mobile 18pt) via FastAPI. Suporta Gradientes e IA Pedagógica. E-Books .docx via FastAPI (Railway). Shortcode: [ebook_generator]
 * Version: 3.0.0
 * Author: Renato Borges
 * Site: professorrenato.com
 */

if (!defined('ABSPATH')) exit;

// Autor: Renato Borges
define('EBOOK_API_URL', 'https://ebook-generator-production-ba9b.up.railway.app/process-full-ebook/');

/**
 * 1. PROXY AJAX SERVER-SIDE
 * Gerencia a comunicação segura com o Backend Python no Railway.
 */
add_action('wp_ajax_gerar_ebook', 'ebook_processar_callback');
add_action('wp_ajax_nopriv_gerar_ebook', 'ebook_processar_callback');

function ebook_processar_callback() {
    check_ajax_referer('ebook_nonce', 'nonce');

    // Sanitização avançada de novos campos (Tela 2)
    $title      = sanitize_text_field($_POST['title'] ?? 'Ebook Gerado');
    $author     = sanitize_text_field($_POST['author'] ?? 'Renato Borges');
    $subtitle   = sanitize_text_field($_POST['subtitle'] ?? '');
    $color1     = sanitize_text_field($_POST['color1'] ?? '#1e3c72');
    $color2     = sanitize_text_field($_POST['color2'] ?? '#2a5298');
    $angle      = intval($_POST['angle'] ?? 45);
    $filename   = sanitize_text_field($_POST['filename'] ?? 'ebook.docx');

    if (empty($_FILES['file']['tmp_name'])) {
        wp_send_json_error('Manuscrito (DOCX/TXT) não detectado.');
    }

    // Preparação Multi-part para FastAPI
    $file_path = $_FILES['file']['tmp_name'];
    $cfile     = new CURLFile($file_path, $_FILES['file']['type'], $_FILES['file']['name']);

    $post_data = [
        'file'      => $cfile,
        'title'     => $title,
        'author'    => $author,
        'subtitle'  => $subtitle,
        'color1'    => $color1,
        'color2'    => $color2,
        'angle'     => $angle,
        'filename'  => $filename
    ];

    $ch = curl_init(EBOOK_API_URL);
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 120, // Aumentado para processamento de IA
        CURLOPT_POSTFIELDS     => $post_data,
    ]);

    $response  = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($http_code !== 200) {
        wp_send_json_error("Erro na Engine Python (Status $http_code).");
    }

    wp_send_json_success([
        'filename' => (strpos($filename, '.docx') !== false) ? $filename : $filename . '.docx',
        'data'     => base64_encode($response),
    ]);
}

/**
 * 2. INTERFACE (SHORTCODE: [ebook_generator])
 * Reflete o design das 3 etapas: Identificação, Capa e Formatação.
 */
add_shortcode('ebook_generator', 'ebook_generator_render_form');

function ebook_generator_render_form() {
    ob_start(); ?>

    <div id="eb_wrapper" style="background-color:#00112E; padding:40px; border-radius:20px; font-family:'Segoe UI', sans-serif; color:#fff; max-width:800px; margin:auto; border:1px solid #1e2d5a; box-shadow:0 20px 50px rgba(0,0,0,0.6);">
        
        <div style="text-align:center; margin-bottom:40px;">
            <h2 style="color:#FFF2B0; font-size:32px; margin-bottom:10px;">🚀 Ebook Pro Generator</h2>
            <p style="color:#a5b1c2; font-size:14px;">Transformação Digital baseada na BNCC da Computação [cite: 1, 2]</p>
        </div>

        <form id="ebookUploadForm">
            <input type="hidden" name="nonce" value="<?php echo wp_create_nonce('ebook_nonce'); ?>">

            <fieldset style="border:none; padding:0; margin-bottom:30px;">
                <legend style="color:#FFF2B0; font-weight:bold; margin-bottom:15px; font-size:18px;">Etapa 1: Manuscrito</legend>
                <input type="text" name="title" placeholder="Título do Ebook" required style="width:100%; padding:15px; margin-bottom:15px; background:#0b1d3a; border:1px solid #1e2d5a; border-radius:8px; color:#fff;">
                <div style="border:2px dashed #1e2d5a; padding:30px; text-align:center; border-radius:10px; background:#0b1d3a;">
                    <input type="file" name="file" accept=".txt,.docx" required>
                    <p style="font-size:12px; color:#a5b1c2; margin-top:10px;">Formatos: DOCX ou TXT</p>
                </div>
            </fieldset>

            <fieldset style="border:none; padding:0; margin-bottom:30px;">
                <legend style="color:#FFF2B0; font-weight:bold; margin-bottom:15px; font-size:18px;">Etapa 2: Design & Capa</legend>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                    <input type="text" name="author" placeholder="Nome do Autor" required style="padding:15px; background:#0b1d3a; border:1px solid #1e2d5a; border-radius:8px; color:#fff;">
                    <input type="text" name="subtitle" placeholder="Subtítulo (Opcional)" style="padding:15px; background:#0b1d3a; border:1px solid #1e2d5a; border-radius:8px; color:#fff;">
                </div>
                <div style="margin-top:15px; display:flex; align-items:center; gap:20px; background:#0b1d3a; padding:15px; border-radius:8px;">
                    <label style="font-size:14px;">Cores do Gradiente:</label>
                    <input type="color" name="color1" value="#1e3c72" style="border:none; height:40px; width:40px; background:none;">
                    <input type="color" name="color2" value="#2a5298" style="border:none; height:40px; width:40px; background:none;">
                    <label style="font-size:14px;">Ângulo:</label>
                    <input type="range" name="angle" min="0" max="360" value="45">
                </div>
            </fieldset>

            <button type="submit" id="eb_btn" style="width:100%; background:linear-gradient(45deg, #FFF2B0, #ffed4a); color:#00112E; border:none; padding:20px; font-size:20px; font-weight:bold; border-radius:50px; cursor:pointer; box-shadow:0 10px 20px rgba(255,242,176,0.2);">
                ⚙️ GERAR E EXPORTAR DOCX (18PT)
            </button>
        </form>

        <div id="eb_status" style="display:none; margin-top:30px; padding:20px; border-radius:10px; text-align:center;"></div>
    </div>

    <script>
    (function() {
        const form = document.getElementById('ebookUploadForm');
        const btn = document.getElementById('eb_btn');
        const status = document.getElementById('eb_status');

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            btn.disabled = true;
            btn.innerText = '🧠 IA PROCESSANDO...';
            status.style.display = 'block';
            status.style.background = '#0b1d3a';
            status.style.color = '#FFF2B0';
            status.innerText = '⏳ Analisando manuscrito e aplicando diretrizes da BNCC Computação... [cite: 1, 3]';

            const formData = new FormData(this);
            formData.append('action', 'gerar_ebook');

            try {
                const response = await fetch('<?php echo admin_url("admin-ajax.php"); ?>', { method: 'POST', body: formData });
                const result = await response.json();

                if (!result.success) throw new Error(result.data);

                status.innerText = '✅ Sucesso! Otimizado para Mobile (18pt).';
                
                const binaryString = window.atob(result.data.data);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) bytes[i] = binaryString.charCodeAt(i);

                const blob = new Blob([bytes], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
                const link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = result.data.filename;
                link.click();

            } catch (error) {
                status.style.color = '#ff6b6b';
                status.innerText = '❌ Erro: ' + error.message;
            } finally {
                btn.disabled = false;
                btn.innerText = '⚙️ GERAR E EXPORTAR DOCX (18PT)';
            }
        });
    })();
    </script>
    <?php return ob_get_clean();
}
