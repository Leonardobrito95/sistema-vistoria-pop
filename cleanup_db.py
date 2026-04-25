import sys
import os

# Adiciona o diretório atual ao sys.path para importar o app locally
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from app import database
except ImportError:
    print("Erro: Não foi possivel importar 'app.database'. Execute o script na raiz do projeto 'sistema infra'.")
    sys.exit(1)

def main():
    db = database.get_db()
    cursor = db.cursor()

    try:
        # Encontrar e deletar duplicatas (mesmo pop_name, mesma descricao, status='pendente')
        # Mantendo apenas a mais recente baseada no 'id' ou 'data_identificacao'
        print("Iniciando limpeza de duplicatas...")
        cursor.execute('''
            DELETE FROM vistoria_pendencias
            WHERE id IN (
                SELECT id
                FROM (
                    SELECT id,
                           ROW_NUMBER() OVER( PARTITION BY pop_name, descricao, status ORDER BY data_identificacao DESC ) as row_num
                    FROM vistoria_pendencias
                    WHERE status = 'pendente'
                ) t
                WHERE t.row_num > 1
            )
        ''')
        deleted_count = cursor.rowcount
        print(f"Sucesso: {deleted_count} pendência(s) duplicada(s) foram apagada(s).")

        # Inserir pendência de teste
        print("Criando pendência de teste...")
        cursor.execute('''
            INSERT INTO vistoria_pendencias (pop_name, categoria, descricao, data_identificacao, status) 
            VALUES ('aguas-claras', 'Limpeza e Organização', 'Teste: Sistema Automático Verificando', CURRENT_TIMESTAMP, 'pendente')
        ''')
        print("Sucesso: Pendência de teste criada para Águas Claras.")

        db.commit()
        print("Todas as alterações salvas no banco de dados com sucesso.")
        
    except Exception as e:
        db.rollback()
        print(f"Ocorreu um erro durante a operação no banco de dados: {e}")
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    main()
