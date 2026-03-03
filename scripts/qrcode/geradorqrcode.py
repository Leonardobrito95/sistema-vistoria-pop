import os
from qrcode import QRCode, constants
from PIL import Image, ImageOps

# Gera o QR Code
qr = QRCode(error_correction=constants.ERROR_CORRECT_H)
qr.add_data("http://172.31.29.10:5001/dashboard?pop=arniqueiras")
qr.make()
img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

# Caminho do logo
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "logo1.png")

# Abre o logo e prepara
logo = Image.open(logo_path).convert("RGBA")

# Adiciona borda branca ao redor do logo
logo = ImageOps.expand(logo, border=10, fill='white')

# Redimensiona o logo (20% do tamanho do QR)
qr_width, qr_height = img_qr.size
logo_size = int(qr_width * 0.2)
logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

# Remove transparência (coloca fundo branco)
bg = Image.new("RGB", logo.size, (255, 255, 255))
bg.paste(logo, mask=logo.split()[3])  # aplica alpha sobre fundo branco

# Calcula posição central
pos = ((qr_width - bg.size[0]) // 2, (qr_height - bg.size[1]) // 2)

# Cola o logo no QR
img_qr.paste(bg, pos)

# Salva o resultado final
output_path = os.path.join(script_dir, "qrcode_com_logo.png")
img_qr.save(output_path)

print(f"✅ QR code gerado com sucesso: {output_path}")
