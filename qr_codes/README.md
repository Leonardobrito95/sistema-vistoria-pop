# QR Codes - Vistoria de POPs

Este diretório contém QR codes para acesso rápido ao dashboard de vistoria de cada POP.

## Arquivos Gerados

- `qr_aguas-claras.png` - QR code para Águas Claras
- `qr_taguatinga.png` - QR code para Taguatinga
- `qr_ceilandia.png` - QR code para Ceilândia
- `qr_arniqueiras.png` - QR code para Arniqueiras
- `qr_sia.png` - QR code para SIA
- `qr_vicente-pires.png` - QR code para Vicente Pires
- `qr_sudoeste.png` - QR code para Sudoeste
- `qr_patio-brasil.png` - QR code para Pátio Brasil

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

- **Águas Claras**: http://45.230.84.50:5002/dashboard?pop=aguas-claras
- **Taguatinga**: http://45.230.84.50:5002/dashboard?pop=taguatinga
- **Ceilândia**: http://45.230.84.50:5002/dashboard?pop=ceilandia
- **Arniqueiras**: http://45.230.84.50:5002/dashboard?pop=arniqueiras
- **SIA**: http://45.230.84.50:5002/dashboard?pop=sia
- **Vicente Pires**: http://45.230.84.50:5002/dashboard?pop=vicente-pires
- **Sudoeste**: http://45.230.84.50:5002/dashboard?pop=sudoeste
- **Pátio Brasil**: http://45.230.84.50:5002/dashboard?pop=patio-brasil


## Regeneração

Para regenerar os QR codes, execute:

```bash
cd w:\sistema infra\scripts
python generate_qr_codes.py
```

---

*Gerado automaticamente pelo sistema de vistoria de POPs*
