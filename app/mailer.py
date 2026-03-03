import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

# Carrega configurações do .env se existirem, caso contrário usa default
load_dotenv('.env')

# --- Configurações SMTP Locaweb ---
SMTP_SERVER = "smtplw.com.br"
SMTP_PORT = 587
SMTP_USER = "canaatelecom"
SMTP_PASSWORD = "Admin01092023" 
SMTP_SENDER = os.getenv("SMTP_SENDER_EMAIL", "contato@canaatelecom.com.br") 
DEFAULT_RECIPIENT = "fernandolima@canaatelecom.com.br, leonardobrito@canaatelecom.com.br"

def _send_email_async(to_email, subject, body_html):
    """Função interna para disparar o e-mail via conexão SMTP na porta 587 (TLS)."""
    
    # Text fallback
    body_text = "Seu leitor de e-mails não suporta HTML. Acesse o painel do sistema para ver o alerta."
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SMTP_SENDER
    msg['To'] = to_email

    part1 = MIMEText(body_text, 'plain', 'utf-8')
    part2 = MIMEText(body_html, 'html', 'utf-8')

    msg.attach(part1)
    msg.attach(part2)

    try:
        # Abre o túnel SMTP com a Locaweb
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() # Criptografia forçada
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        # Dispara
        server.send_message(msg)
        server.quit()
        print(f"[MAILER SMTPLW] E-mail '{subject}' enviado com sucesso para {to_email}")
    except Exception as e:
        print(f"[MAILER SMTPLW] Erro crasso do servidor SMTP ao enviar alerta para {to_email}:\n{e}")

def send_expiration_alert(pop_name, item_name, data_venc, status_atual, to_email=DEFAULT_RECIPIENT):
    """
    Template 1: Alerta de Vencimento de Status
    """
    subject = f"⚠️ Alerta: Vencimento próximo no POP {pop_name}"
    
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h3 style="color: #d9534f;">Olá,</h3>
        <p>O status do item <strong>{item_name}</strong> no POP <strong>{pop_name}</strong> está exigindo atenção.</p>
        <ul style="border-left: 3px solid #f0ad4e; padding-left: 15px;">
            <li><strong>Data de Vencimento:</strong> {data_venc}</li>
            <li><strong>Status Atual:</strong> {status_atual}</li>
        </ul>
        <p>Acesse o painel do sistema para programar a regularização.</p>
      </body>
    </html>
    """
    threading.Thread(target=_send_email_async, args=(to_email, subject, body_html)).start()

def send_maintenance_update(pop_name, item_name, novo_status, to_email=DEFAULT_RECIPIENT):
    """
    Template 2: Alerta de Status de Manutenção Atualizada
    """
    subject = f"🔄 Atualização: Manutenção no POP {pop_name}"
    data_hora = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h3 style="color: #0275d8;">Olá,</h3>
        <p>O status de manutenção do POP <strong>{pop_name}</strong> foi atualizado com sucesso no sistema.</p>
        <ul style="border-left: 3px solid #5cb85c; padding-left: 15px;">
            <li><strong>Item Atualizado:</strong> {item_name}</li>
            <li><strong>Novo Status:</strong> {novo_status}</li>
            <li><strong>Data da Atualização:</strong> {data_hora}</li>
        </ul>
        <p>Acesse o dashboard de vistorias para visualizar todos os detalhes.</p>
      </body>
    </html>
    """
    threading.Thread(target=_send_email_async, args=(to_email, subject, body_html)).start()

def send_mass_maintenance_update(pop_name, updated_items_list, to_email=DEFAULT_RECIPIENT):
    """
    Template 2 (Massivo): Alerta Condensado de Status de Manutenção
    """
    if not updated_items_list:
        return
        
    subject = f"🔄 Atualização Múltipla: Manutenção no POP {pop_name}"
    data_hora = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    items_html = ""
    for item in updated_items_list:
        items_html += f"<li><strong>{item['nome']}:</strong> {item['status']}</li>"
    
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h3 style="color: #0275d8;">Olá,</h3>
        <p>A vistoria do POP <strong>{pop_name}</strong> acabou de renovar os seguintes status de manutenção no sistema:</p>
        <ul style="border-left: 3px solid #5cb85c; padding-left: 15px;">
            {items_html}
            <li style="margin-top: 10px; color: #666; font-size: 0.9em;"><strong>Data da Atualização:</strong> {data_hora}</li>
        </ul>
        <p>Acesse o dashboard de vistorias para visualizar todos os detalhes.</p>
      </body>
    </html>
    """
    threading.Thread(target=_send_email_async, args=(to_email, subject, body_html)).start()

def send_pendency_resolved(pop_name, descricao_pendencia, resolved_by, to_email=DEFAULT_RECIPIENT):
    """
    Template 3: Pendência Resolvida
    """
    subject = f"✅ Resolvido: Pendência no POP {pop_name}"
    data_hora = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h3 style="color: #5cb85c;">Olá,</h3>
        <p>Uma pendência técnica acaba de ser marcada como resolvida pela equipe.</p>
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
            <p style="margin: 5px 0;"><strong>📍 POP:</strong> {pop_name}</p>
            <p style="margin: 5px 0;"><strong>🛠️ Serviço Realizado:</strong> {descricao_pendencia}</p>
            <p style="margin: 5px 0;"><strong>👤 Resolvido por:</strong> {resolved_by}</p>
            <p style="margin: 5px 0;"><strong>🕒 Data da Confirmação:</strong> {data_hora}</p>
        </div>
      </body>
    </html>
    """
    threading.Thread(target=_send_email_async, args=(to_email, subject, body_html)).start()
