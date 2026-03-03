import os
import resend
from dotenv import load_dotenv

print("==========================================")
print(" Testando conexão API Resend (resend.com) ")
print("==========================================")

load_dotenv('.env')
API_KEY = os.getenv("RESEND_API_KEY")

if not API_KEY or len(API_KEY) < 10:
    print("❌ ERRO: Você esqueceu de colar a chave no arquivo .env!")
    exit(1)

resend.api_key = API_KEY
sender_email = os.getenv("RESEND_SENDER_EMAIL", "onboarding@resend.dev")
recipient_email = "leonardobrito@canaatelecom.com.br"

try:
    print(f"-> Disparando E-mail via POST da API para {recipient_email}...")
    
    response = resend.Emails.send({
        "from": f"Sistema Infra <{sender_email}>",
        "to": recipient_email,
        "subject": "🚀 Teste de Conexão Resend API",
        "html": "<h3>Sucesso Absoluto!</h3><p>O seu código <b>Python</b> se conectou perfeitamente com a API super rápida do Resend.</p>"
    })
    
    print(f"\n✅ SUCESSO EXTREMO! E-mail enfileirado e disparado no Resend.")
    print(f"ID devolvido pelo servidor: {response.get('id')}")

except Exception as e:
    print(f"\n❌ FALHA AO CHAMAR A API! Detalhes:\n{e}")
