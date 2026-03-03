"""
Script para gerar QR codes para cada região POP.
Cada QR code direciona para o dashboard filtrado por POP.
"""

import qrcode
import os

# URL base do dashboard
BASE_URL = "http://45.230.84.50:5002/dashboard?pop="

# Lista de POPs
POPS = [
    "aguas-claras",
    "taguatinga",
    "ceilandia",
    "arniqueiras",
    "sia",
    "vicente-pires",
    "sudoeste",
    "patio-brasil"
]

# Nomes formatados para exibição
POP_DISPLAY_NAMES = {
    "aguas-claras": "Águas Claras",
    "taguatinga": "Taguatinga",
    "ceilandia": "Ceilândia",
    "arniqueiras": "Arniqueiras",
    "sia": "SIA",
    "vicente-pires": "Vicente Pires",
    "sudoeste": "Sudoeste",
    "patio-brasil": "Pátio Brasil"
}

def generate_qr_codes():
    """Gera QR codes para todos os POPs."""
    
    # Cria diretório para os QR codes
    qr_dir = os.path.join(os.path.dirname(__file__), '..', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    print("=" * 80)
    print("GERAÇÃO DE QR CODES PARA POPs")
    print("=" * 80)
    print(f"Diretório de saída: {qr_dir}")
    print()
    
    generated_files = []
    
    for pop in POPS:
        # URL completa para este POP
        url = BASE_URL + pop
        
        # Cria o QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Gera a imagem
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Salva o arquivo
        filename = f"qr_{pop}.png"
        filepath = os.path.join(qr_dir, filename)
        img.save(filepath)
        
        generated_files.append({
            'pop': pop,
            'display_name': POP_DISPLAY_NAMES[pop],
            'filename': filename,
            'url': url
        })
        
        print(f"✓ {POP_DISPLAY_NAMES[pop]}: {filename}")
        print(f"  URL: {url}")
    
    # Gera arquivo HTML com todos os QR codes para impressão
    html_content = generate_html_index(generated_files)
    html_path = os.path.join(qr_dir, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✓ Arquivo HTML gerado: index.html")
    
    # Gera README
    readme_content = generate_readme()
    readme_path = os.path.join(qr_dir, 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✓ README gerado: README.md")
    
    print("\n" + "=" * 80)
    print(f"✓ {len(POPS)} QR codes gerados com sucesso!")
    print("=" * 80)
    print(f"\nPara visualizar todos os QR codes, abra: {html_path}")

def generate_html_index(files):
    """Gera arquivo HTML com todos os QR codes para impressão."""
    
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Codes - Vistoria POPs</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 40px;
        }
        .qr-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        .qr-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            page-break-inside: avoid;
        }
        .qr-card h2 {
            margin-top: 0;
            color: #2c3e50;
            font-size: 24px;
        }
        .qr-card img {
            max-width: 100%;
            height: auto;
            margin: 20px 0;
        }
        .qr-card .url {
            font-size: 12px;
            color: #7f8c8d;
            word-break: break-all;
            margin-top: 10px;
        }
        .instructions {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .instructions h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .instructions ol {
            line-height: 1.8;
        }
        @media print {
            body {
                background: white;
            }
            .instructions {
                page-break-after: always;
            }
            .qr-card {
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <h1>🔍 QR Codes - Vistoria de POPs</h1>
    
    <div class="instructions">
        <h3>📋 Instruções de Uso</h3>
        <ol>
            <li>Cada QR code abaixo direciona para o dashboard de vistoria filtrado por POP</li>
            <li>Escaneie o QR code com seu smartphone para acessar rapidamente as informações do POP</li>
            <li>Os QR codes podem ser impressos e afixados em cada local físico do POP</li>
            <li>Para imprimir, use Ctrl+P ou Cmd+P e selecione a opção de impressão</li>
        </ol>
    </div>
    
    <div class="qr-grid">
"""
    
    for file_info in files:
        html += f"""
        <div class="qr-card">
            <h2>{file_info['display_name']}</h2>
            <img src="{file_info['filename']}" alt="QR Code {file_info['display_name']}">
            <div class="url">{file_info['url']}</div>
        </div>
"""
    
    html += """
    </div>
    
    <footer style="text-align: center; color: #7f8c8d; margin-top: 40px;">
        <p>Sistema de Vistoria de POPs - Gerado automaticamente</p>
    </footer>
</body>
</html>
"""
    
    return html

def generate_readme():
    """Gera arquivo README com instruções."""
    
    readme = """# QR Codes - Vistoria de POPs

Este diretório contém QR codes para acesso rápido ao dashboard de vistoria de cada POP.

## Arquivos Gerados

"""
    
    for pop in POPS:
        readme += f"- `qr_{pop}.png` - QR code para {POP_DISPLAY_NAMES[pop]}\n"
    
    readme += """
- `index.html` - Página HTML com todos os QR codes para visualização e impressão
- `README.md` - Este arquivo

## Como Usar

### Visualização

Abra o arquivo `index.html` em qualquer navegador para ver todos os QR codes.

### Impressão

1. Abra `index.html` no navegador
2. Use Ctrl+P (Windows/Linux) ou Cmd+P (Mac)
3. Configure a impressão conforme necessário
4. Imprima os QR codes

### Instalação nos POPs

1. Imprima os QR codes
2. Plastifique ou proteja os QR codes impressos
3. Afixe cada QR code no local correspondente do POP
4. Os técnicos podem escanear o QR code para acessar rapidamente as informações

## URLs dos QR Codes

"""
    
    for pop in POPS:
        url = BASE_URL + pop
        readme += f"- **{POP_DISPLAY_NAMES[pop]}**: {url}\n"
    
    readme += """

## Regeneração

Para regenerar os QR codes, execute:

```bash
cd w:\\sistema infra\\scripts
python generate_qr_codes.py
```

---

*Gerado automaticamente pelo sistema de vistoria de POPs*
"""
    
    return readme

if __name__ == '__main__':
    generate_qr_codes()
