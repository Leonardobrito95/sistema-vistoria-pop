"""
Script para resetar a senha do usuário admin.
Execute: python scripts/reset_admin_password.py
"""

import sys
import os
import getpass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import database
from werkzeug.security import generate_password_hash

print("=" * 80)
print("RESET DE SENHA DO USUÁRIO ADMIN")
print("=" * 80)

admin_user = database.get_user_by_username('admin')

new_password = getpass.getpass("\nNova senha para o admin: ")
confirm = getpass.getpass("Confirme a nova senha: ")

if new_password != confirm:
    print("\n✗ As senhas não coincidem. Operação cancelada.")
    sys.exit(1)

if len(new_password) < 8:
    print("\n✗ A senha deve ter pelo menos 8 caracteres.")
    sys.exit(1)

new_hash = generate_password_hash(new_password, method='pbkdf2:sha256')

if admin_user:
    print(f"\nUsuário encontrado: {admin_user['name']}")
    database.update_user_password(admin_user['id'], new_hash)
    print("✓ Senha do usuário admin atualizada com sucesso!")
else:
    print("\nUsuário admin não encontrado. Criando...")
    database.create_user('admin', new_hash, 'Administrador do Sistema', True)
    print("✓ Usuário admin criado com sucesso!")

print("\n" + "=" * 80)
print("CONCLUÍDO")
print("=" * 80)
