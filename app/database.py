import psycopg2
import psycopg2.extras
from datetime import datetime
import os
from werkzeug.security import generate_password_hash

from dotenv import load_dotenv

_basedir = os.path.abspath(os.path.dirname(__file__))
# Carrega variáveis de ambiente do arquivo .env, se existir
load_dotenv(os.path.join(_basedir, '..', '.env'))

DB_HOST = os.getenv('DB_HOST', '172.31.29.10')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'sistema_db')
DB_USER = os.getenv('DB_USER', 'datacanaa')
DB_PASS = os.getenv('DB_PASS', '21#canaa@23')

DATABASE_URL = f"host='{DB_HOST}' port='{DB_PORT}' dbname='{DB_NAME}' user='{DB_USER}' password='{DB_PASS}'"

def get_db():
    """Estabelece conexão com o banco de dados PostgreSQL."""
    db = psycopg2.connect(DATABASE_URL)
    return db

def init_db():
    """Inicializa o banco de dados com o schema do PostgreSQL."""
    with get_db() as db:
        with db.cursor() as cursor:
            with open(os.path.join(_basedir, '..', 'data', 'schema.sql'), 'r') as f:
                cursor.execute(f.read())
    print("Banco de dados inicializado.")

def add_submission(pop_name, inspector_name, submission_time, form_data, photos):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO vistoria_pop (pop_name, inspector_name, submission_time, form_data, photos) VALUES (%s, %s, %s, %s, %s)',
        (pop_name, inspector_name, submission_time, form_data, photos)
    )
    db.commit()





def get_last_update_for_each_pop():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """
        SELECT pop_name, MAX(submission_time) as last_update
        FROM vistoria_pop
        GROUP BY pop_name
    """
    cursor.execute(query)
    return {row['pop_name']: row['last_update'].strftime('%d/%m/%Y - %H:%M') for row in cursor.fetchall()}

def get_all_submissions(filter_pop=None, filter_date=None):
    """Retorna todas as vistorias, ordenadas por data."""
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    query = 'SELECT * FROM vistoria_pop'
    params = []
    conditions = []
    
    if filter_pop:
        conditions.append('pop_name = %s')
        params.append(filter_pop)
        
    if filter_date:
        conditions.append("submission_time::date = %s")
        params.append(filter_date)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
        
    query += ' ORDER BY submission_time DESC'
    
    cursor.execute(query, params)
    return cursor.fetchall()

def get_latest_submission_per_pop(filter_pop=None):
    """Retorna o último formulário submetido de cada POP, independente da data."""
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if filter_pop:
        cursor.execute('''
            SELECT DISTINCT ON (pop_name) 
                submission_id, pop_name, inspector_name, 
                submission_time, form_data, photos
            FROM vistoria_pop
            WHERE pop_name = %s
            ORDER BY pop_name, submission_time DESC
        ''', (filter_pop,))
    else:
        cursor.execute('''
            SELECT DISTINCT ON (pop_name) 
                submission_id, pop_name, inspector_name, 
                submission_time, form_data, photos
            FROM vistoria_pop
            ORDER BY pop_name, submission_time DESC
        ''')
    
    return cursor.fetchall()

def get_maintenance_info_for_pops():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    maintenance_checks = {
        'bateria': ('baterias', ['baterias_trocadas', 'Baterias Trocadas']),
        'gerador': ('gerador', ['gerador_manut_periodica_realizada', 'Realizado Manutenção periódica do Gerador']),
        'ar_condicionado': ('ar_condicionado', ['ar_manut_periodica_realizada', 'Realizado Manutenção periódica do Ar']),
        'limpeza': ('limpeza', ['limpeza_periodica_realizada', 'Realizado Limpeza periódica']),
        'bateria_gerador': ('gerador', ['gerador_bateria_trocada', 'Bateria do gerador trocada']),
        'teste_bateria': ('baterias', ['baterias_ok', 'Baterias testadas e funcionando corretamente', 'Baterias testadas e funcionando'])
    }

    results = {}
    for key, (field, values) in maintenance_checks.items():
        where_clauses = []
        params = []
        
        for value in values:
            where_clauses.append(f"form_data->%s @> to_jsonb(%s::text)")
            params.extend([field, value])
            
        where_condition = " OR ".join(where_clauses)
        
        query = f"""
            SELECT pop_name, MAX(submission_time) as last_date
            FROM vistoria_pop
            WHERE {where_condition}
            GROUP BY pop_name
        """
        
        cursor.execute(query, params)
        results[key] = {row['pop_name']: row['last_date'] for row in cursor.fetchall()}
    return results

def get_submission(submission_id):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM vistoria_pop WHERE submission_id = %s', (submission_id,))
    return cursor.fetchone()

def delete_submission(submission_id):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT photos FROM vistoria_pop WHERE submission_id = %s', (submission_id,))
    row = cursor.fetchone()
    
    cursor.execute('DELETE FROM vistoria_pop WHERE submission_id = %s', (submission_id,))
    db.commit()

    if row and row['photos']:
        upload_folder = os.path.abspath(os.path.join(_basedir, '..', 'data', 'uploads'))
        for relative_path in row['photos']:
            full_path = os.path.join(upload_folder, relative_path.replace('/', os.sep))
            if os.path.exists(full_path):
                os.remove(full_path)

def update_submission(submission_id, form_data, photos):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'UPDATE vistoria_pop SET form_data = %s, photos = %s WHERE submission_id = %s',
        (form_data, photos, submission_id)
    )
    db.commit()

def get_user_by_id(user_id):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM vistoria_user WHERE id = %s', (user_id,))
    return cursor.fetchone()

def get_user_by_username(username):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM vistoria_user WHERE username = %s', (username,))
    return cursor.fetchone()

def get_all_users():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM vistoria_user ORDER BY name')
    return [dict(row) for row in cursor.fetchall()]

def create_user(username, password_hash, name, is_admin, is_supervisor=False):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO vistoria_user (username, password, name, is_admin, is_supervisor) VALUES (%s, %s, %s, %s, %s)',
        (username, password_hash, name, is_admin, is_supervisor)
    )
    db.commit()

def update_user(user_id, username, name, is_admin, is_supervisor=False):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'UPDATE vistoria_user SET username = %s, name = %s, is_admin = %s, is_supervisor = %s WHERE id = %s',
        (username, name, is_admin, is_supervisor, user_id)
    )
    db.commit()

def update_user_password(user_id, password_hash):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE vistoria_user SET password = %s WHERE id = %s', (password_hash, user_id))
    db.commit()

def delete_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM vistoria_user WHERE id = %s', (user_id,))
    db.commit()

def create_initial_admin_user():
    if not get_user_by_username('admin'):
        print("Criando usuário 'admin' inicial...")
        create_user('admin', generate_password_hash('CNT@@##2025', method='pbkdf2:sha256'), 'Administrador do Sistema', True)

def cleanup_old_submissions():
    """Exclui submissões e fotos com mais de 30 dias."""
    import os
    
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT submission_id, photos FROM vistoria_pop WHERE submission_time::date < (CURRENT_DATE - INTERVAL '365 days')")
    old_submissions = cursor.fetchall()

    if not old_submissions:
        print("Nenhuma submissão antiga para limpar.")
        return

    print(f"Limpando {len(old_submissions)} submissões antigas...")
    for sub in old_submissions:
        delete_submission(sub['submission_id'])
    
    print("Limpeza de submissões antigas concluída.")

def get_pendencias_by_pop(pop_name=None, status=None):
    """Retorna pendências filtradas por POP e/ou status."""
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    query = "SELECT * FROM vistoria_pendencias WHERE 1=1"
    params = []
    
    if pop_name:
        query += " AND pop_name = %s"
        params.append(pop_name)
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    query += " ORDER BY data_identificacao DESC"
    
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

def pendencia_exists(pop_name, categoria, descricao):
    """Verifica se já existe uma pendência aberta idêntica para não duplicar."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT 1 FROM vistoria_pendencias WHERE pop_name = %s AND categoria = %s AND descricao = %s AND status = 'pendente'",
        (pop_name, categoria, descricao)
    )
    return cursor.fetchone() is not None

def add_pendencia(pop_name, categoria, descricao, data_identificacao, submission_id=None, observacoes=None):
    """Adiciona uma nova pendência."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO vistoria_pendencias (pop_name, categoria, descricao, data_identificacao, submission_id, observacoes) VALUES (%s, %s, %s, %s, %s, %s)',
        (pop_name, categoria, descricao, data_identificacao, submission_id, observacoes)
    )
    db.commit()

def resolve_pendencia(pendencia_id, data_resolucao, resolved_by, observacoes=None):
    """Marca uma pendência como resolvida."""
    db = get_db()
    cursor = db.cursor()
    
    update_query = 'UPDATE vistoria_pendencias SET status = %s, data_resolucao = %s, resolved_by = %s'
    params = ['resolvido', data_resolucao, resolved_by]
    
    if observacoes:
        update_query += ', observacoes = %s'
        params.append(observacoes)
    
    update_query += ' WHERE id = %s'
    params.append(pendencia_id)
    
    cursor.execute(update_query, params)
    db.commit()

def get_pendencias_abertas():
    """Retorna todas as pendências em aberto agrupadas por POP."""
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    query = """
        SELECT * FROM vistoria_pendencias 
        WHERE status = 'pendente'
        ORDER BY pop_name, data_identificacao DESC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    pendencias_por_pop = {}
    for row in rows:
        pop = row['pop_name']
        if pop not in pendencias_por_pop:
            pendencias_por_pop[pop] = []
        pendencias_por_pop[pop].append(dict(row))
    
    return pendencias_por_pop

def get_pendencias_resolvidas():
    """Retorna todas as pendências resolvidas."""
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    query = """
        SELECT * FROM vistoria_pendencias 
        WHERE status = 'resolvido'
        ORDER BY data_resolucao DESC
    """
    
    cursor.execute(query)
    return [dict(row) for row in cursor.fetchall()]

def get_pendencias_stats():
    """Retorna estatísticas sobre pendências."""
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT COUNT(*) as total FROM vistoria_pendencias WHERE status = 'pendente'")
    total_abertas = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM vistoria_pendencias WHERE status = 'resolvido'")
    total_resolvidas = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT categoria, COUNT(*) as total 
        FROM vistoria_pendencias 
        WHERE status = 'pendente'
        GROUP BY categoria
        ORDER BY total DESC
    """)
    por_categoria = {row['categoria']: row['total'] for row in cursor.fetchall()}
    
    cursor.execute("""
        SELECT pop_name, COUNT(*) as total 
        FROM vistoria_pendencias 
        WHERE status = 'pendente'
        GROUP BY pop_name
        ORDER BY total DESC
    """)
    por_pop = {row['pop_name']: row['total'] for row in cursor.fetchall()}
    
    return {
        'total_abertas': total_abertas,
        'total_resolvidas': total_resolvidas,
        'por_categoria': por_categoria,
        'por_pop': por_pop
    }

if __name__ == '__main__':
    print("Inicializando o banco de dados...")
    init_db()