"""
Script para atualizar o status de manutenção com base nos dados migrados do Excel.
Este script processa as últimas vistorias de cada POP e atualiza os campos relevantes
para que apareçam no status de manutenção.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import database

print("=" * 80)
print("ATUALIZAÇÃO DE STATUS DE MANUTENÇÃO")
print("=" * 80)

# Mapeamento de campos do Excel para campos de manutenção
MAINTENANCE_MAPPINGS = {
    'baterias': {
        'keywords': ['Baterias testadas e funcionando corretamente', 'Bateria', 'bateria'],
        'target_field': 'baterias',
        'target_value': 'Baterias Trocadas'
    },
    'gerador': {
        'keywords': ['Teste de acionamento manual', 'gerador', 'Gerador'],
        'target_field': 'gerador',
        'target_value': 'Realizado Manutenção periódica do Gerador'
    },
    'ar_condicionado': {
        'keywords': ['Ar condicionado', 'ar condicionado', 'Temperatura'],
        'target_field': 'ar_condicionado',
        'target_value': 'Realizado Manutenção periódica do Ar'
    },
    'limpeza': {
        'keywords': ['Espaço Limpo e organizado', 'Limpeza', 'limpeza'],
        'target_field': 'limpeza',
        'target_value': 'Realizado Limpeza periódica'
    }
}

# Busca as últimas vistorias de cada POP
db = database.get_db()
cursor = db.cursor()

# Busca a última vistoria de cada POP
query = """
    SELECT DISTINCT ON (pop_name) 
        submission_id, pop_name, submission_time, form_data
    FROM vistoria_pop
    ORDER BY pop_name, submission_time DESC
"""

cursor.execute(query)
vistorias = cursor.fetchall()

print(f"\nEncontradas {len(vistorias)} vistorias (última de cada POP)")

updates_count = 0

for vistoria in vistorias:
    submission_id, pop_name, submission_time, form_data = vistoria
    
    print(f"\n--- {pop_name.upper()} ---")
    print(f"Data da vistoria: {submission_time}")
    
    # Converte form_data de JSON para dict se necessário
    if isinstance(form_data, str):
        import json
        form_data = json.loads(form_data)
    
    # Verifica cada tipo de manutenção
    for maint_type, config in MAINTENANCE_MAPPINGS.items():
        # Verifica se algum campo do form_data contém as palavras-chave
        found = False
        for field_name, field_value in form_data.items():
            if isinstance(field_value, str):
                for keyword in config['keywords']:
                    if keyword.lower() in field_value.lower():
                        found = True
                        break
            if found:
                break
        
        if found:
            # Atualiza o form_data para incluir o campo de manutenção
            form_data[config['target_field']] = config['target_value']
            print(f"  ✓ {maint_type}: Adicionado campo de manutenção")
            updates_count += 1
    
    # Atualiza o registro no banco
    import json
    cursor.execute(
        'UPDATE vistoria_pop SET form_data = %s WHERE submission_id = %s',
        (json.dumps(form_data), submission_id)
    )

db.commit()

print("\n" + "=" * 80)
print(f"✓ Atualização concluída!")
print(f"  Total de campos de manutenção adicionados: {updates_count}")
print("=" * 80)
print("\nAgora o status de manutenção no dashboard deve exibir as informações corretas.")
