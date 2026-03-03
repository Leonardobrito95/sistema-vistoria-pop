"""
Script para resetar a senha do usuário admin.
"""

import sys
import os

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import database
from werkzeug.security import generate_password_hash

print("=" * 80)
print("RESET DE SENHA DO USUÁRIO ADMIN")
print("=" * 80)

# Busca o usuário admin
admin_user = database.get_user_by_username('admin')

if admin_user:
    print(f"\nUsuário encontrado: {admin_user['name']}")
    print(f"Username: {admin_user['username']}")
    
    # Gera novo hash de senha
    new_password = 'CNT@@##2025'
    new_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
    
    print(f"\nGerando novo hash de senha...")
    
    # Atualiza a senha
    database.update_user_password(admin_user['id'], new_hash)
    
    print(f"✓ Senha do usuário admin atualizada com sucesso!")
    print(f"  Nova senha: {new_password}")
    print(f"  Método de hash: pbkdf2:sha256")
else:
    print("\n✗ Usuário admin não encontrado!")
    print("Criando usuário admin...")
    
    password_hash = generate_password_hash('CNT@@##2025', method='pbkdf2:sha256')
    database.create_user('admin', password_hash, 'Administrador do Sistema', True)
    
    print("✓ Usuário admin criado com sucesso!")
    print("  Username: admin")
    print("  Senha: CNT@@##2025")

print("\n" + "=" * 80)
print("CONCLUÍDO")
print("=" * 80)
