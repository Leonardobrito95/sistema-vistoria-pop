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
DEFAULT_RECIPIENT = "fernandolima@canaatelecom.com.br"

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
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
      <div style="background-color: #d32f2f; color: white; padding: 15px 20px;">
        <h2 style="margin: 0; font-size: 18px;">⚠️ Alerta de Vencimento: POP {pop_name}</h2>
      </div>
      <div style="padding: 20px;">
        <p style="margin-top: 0;">Olá, equipe.</p>
        <p>O status de um item está exigindo atenção (próximo ao vencimento ou vencido):</p>
        <div style="background-color: #fff8e1; padding: 15px; border-left: 4px solid #fbc02d; border-radius: 4px; margin-bottom: 20px;">
          <p style="margin: 0 0 10px 0;">📌 <strong>Item:</strong> {item_name}</p>
          <p style="margin: 0 0 10px 0;">📅 <strong>Vencimento:</strong> <span style="color: #d32f2f; font-weight: bold;">{data_venc}</span></p>
          <p style="margin: 0;">⚠️ <strong>Status Atual:</strong> {status_atual}</p>
        </div>
        <div style="text-align: center; margin: 30px 0 10px 0;">
          <a href="http://45.230.84.50:5002/dashboard" style="background-color: #0056b3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">Acessar Dashboard de Vistorias</a>
        </div>
      </div>
      <div style="background-color: #f4f4f4; color: #777; text-align: center; padding: 12px; font-size: 11px;">
        Este é um e-mail automático gerado pelo Sistema de Vistorias. Por favor, não responda.<br>
        © {datetime.now().year} Departamento de TI - Canaã Telecom
      </div>
    </div>
    """
    threading.Thread(target=_send_email_async, args=(to_email, subject, body_html)).start()

def send_maintenance_update(pop_name, item_name, novo_status, to_email=DEFAULT_RECIPIENT):
    """
    Template 2: Alerta de Status de Manutenção Atualizada
    """
    subject = f"🔄 Atualização: Manutenção no POP {pop_name}"
    data_hora = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    body_html = f"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
      <div style="background-color: #2e7d32; color: white; padding: 15px 20px;">
        <h2 style="margin: 0; font-size: 18px;">✅ Status de Manutenção: POP {pop_name}</h2>
      </div>
      <div style="padding: 20px;">
        <p style="margin-top: 0;">Olá, equipe.</p>
        <p>Um status de manutenção foi atualizado no sistema:</p>
        <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4CAF50; border-radius: 4px; margin-bottom: 20px;">
          <p style="margin: 0 0 10px 0;">📌 <strong>{item_name}:</strong> <span style="color: #2e7d32; font-weight: bold;">{novo_status}</span></p>
          <p style="margin: 0; font-size: 12px; color: #666;">📅 <strong>Data da Atualização:</strong> {data_hora}</p>
        </div>
        <div style="text-align: center; margin: 30px 0 10px 0;">
          <a href="http://45.230.84.50:5002/dashboard" style="background-color: #0056b3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">Acessar Dashboard de Vistorias</a>
        </div>
      </div>
      <div style="background-color: #f4f4f4; color: #777; text-align: center; padding: 12px; font-size: 11px;">
        Este é um e-mail automático gerado pelo Sistema de Vistorias. Por favor, não responda.<br>
        © {datetime.now().year} Departamento de TI - Canaã Telecom
      </div>
    </div>
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
        items_html += f'<p style="margin: 0 0 10px 0;">📌 <strong>{item["nome"]}:</strong> <span style="color: #2e7d32; font-weight: bold;">{item["status"]}</span></p>\n'
    
    body_html = f"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
      <div style="background-color: #2e7d32; color: white; padding: 15px 20px;">
        <h2 style="margin: 0; font-size: 18px;">✅ Status de Manutenção: POP {pop_name}</h2>
      </div>
      <div style="padding: 20px;">
        <p style="margin-top: 0;">Olá, equipe.</p>
        <p>A vistoria foi finalizada e os seguintes status de manutenção foram atualizados no sistema:</p>
        <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4CAF50; border-radius: 4px; margin-bottom: 20px;">
          {items_html}
          <p style="margin: 0; font-size: 12px; color: #666;">📅 <strong>Data da Atualização:</strong> {data_hora}</p>
        </div>
        <div style="text-align: center; margin: 30px 0 10px 0;">
          <a href="http://45.230.84.50:5002/dashboard" style="background-color: #0056b3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">Acessar Dashboard de Vistorias</a>
        </div>
      </div>
      <div style="background-color: #f4f4f4; color: #777; text-align: center; padding: 12px; font-size: 11px;">
        Este é um e-mail automático gerado pelo Sistema de Vistorias. Por favor, não responda.<br>
        © {datetime.now().year} Departamento de TI - Canaã Telecom
      </div>
    </div>
    """
    threading.Thread(target=_send_email_async, args=(to_email, subject, body_html)).start()

def send_pendency_resolved(pop_name, descricao_pendencia, resolved_by, to_email=DEFAULT_RECIPIENT):
    """
    Template 3: Pendência Resolvida
    """
    subject = f"✅ Resolvido: Pendência no POP {pop_name}"
    data_hora = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    body_html = f"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
      <div style="background-color: #1976d2; color: white; padding: 15px 20px;">
        <h2 style="margin: 0; font-size: 18px;">✅ Pendência Resolvida: POP {pop_name}</h2>
      </div>
      <div style="padding: 20px;">
        <p style="margin-top: 0;">Olá, equipe.</p>
        <p>Uma pendência técnica acaba de ser marcada como resolvida no sistema.</p>
        <div style="background-color: #f0f8ff; padding: 15px; border-left: 4px solid #1976d2; border-radius: 4px; margin-bottom: 20px;">
          <p style="margin: 0 0 10px 0;">📍 <strong>POP:</strong> {pop_name}</p>
          <p style="margin: 0 0 10px 0;">🛠️ <strong>Serviço Realizado:</strong> {descricao_pendencia}</p>
          <p style="margin: 0 0 10px 0;">👤 <strong>Resolvido por:</strong> {resolved_by}</p>
          <p style="margin: 0; font-size: 12px; color: #666;">🕒 <strong>Data da Confirmação:</strong> {data_hora}</p>
        </div>
        <div style="text-align: center; margin: 30px 0 10px 0;">
          <a href="http://45.230.84.50:5002/dashboard" style="background-color: #0056b3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">Acessar Dashboard de Vistorias</a>
        </div>
      </div>
      <div style="background-color: #f4f4f4; color: #777; text-align: center; padding: 12px; font-size: 11px;">
        Este é um e-mail automático gerado pelo Sistema de Vistorias. Por favor, não responda.<br>
        © {datetime.now().year} Departamento de TI - Canaã Telecom
      </div>
    </div>
    """
    threading.Thread(target=_send_email_async, args=(to_email, subject, body_html)).start()
