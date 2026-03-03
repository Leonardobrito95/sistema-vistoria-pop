import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import threading
from datetime import datetime, timedelta
from . import database
from . import mailer

app = Flask(__name__)

login_manager: LoginManager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "warning"

class User(UserMixin):
    """Modelo de usuário para o Flask-Login."""
    def __init__(self, id, username, password_hash, name, is_admin=False, is_supervisor=False):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.name = name
        self.is_admin = is_admin
        self.is_supervisor = is_supervisor

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    """Carrega um usuário pelo ID."""
    user_data = database.get_user_by_id(user_id)
    if user_data:
        return User(
            id=user_data['id'], 
            username=user_data['username'], 
            password_hash=user_data['password'], 
            name=user_data['name'], 
            is_admin=user_data['is_admin'],
            is_supervisor=user_data.get('is_supervisor', False)
        )
    return None

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key-trocar-em-producao')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

POPS = [
    "aguas-claras", "taguatinga", "ceilandia", "arniqueiras",
    "sia", "vicente-pires", "sudoeste", "patio-brasil"
]

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

database.init_db()
database.create_initial_admin_user()
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
database.cleanup_old_submissions()

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = database.get_user_by_username(username)
        
        if user_data:
            user = User(
                id=user_data['id'], 
                username=user_data['username'], 
                password_hash=user_data['password'], 
                name=user_data['name'], 
                is_admin=user_data['is_admin'],
                is_supervisor=user_data.get('is_supervisor', False)
            )
            if user.check_password(password):
                login_user(user)
                return redirect(url_for('dashboard'))

        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Faz o logout do usuário."""
    logout_user()
    return redirect(url_for('login'))

@app.route('/pop/<pop_name>', methods=['GET', 'POST'])
@login_required
def pop_form(pop_name):
    """Exibe e processa o formulário de vistoria para um POP."""
    if pop_name not in POPS:
        return "POP não encontrado", 404

    if request.method == 'POST':
        form_data = {}
        for key, values in request.form.lists():
            if key.endswith('_outro'):
                main_key = key.replace('_outro', '')
                non_empty_values = [v for v in values if v.strip()]
                if non_empty_values:
                    if main_key in form_data:
                        if not isinstance(form_data[main_key], list):
                            form_data[main_key] = [form_data[main_key]]
                        form_data[main_key].extend(non_empty_values)
                    else:
                        form_data[main_key] = non_empty_values
            elif len(values) == 1:
                form_data[key] = values[0]
            else:
                form_data[key] = values

        required_fields = ['limpeza', 'ar_condicionado', 'gerador', 'baterias', 'rede_eletrica', 'retificadoras', 'amperagem_rack_01']
        missing_fields = []
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                missing_fields.append(field)
                
        text_fields = ['amperagem_rack_01']
        for field in text_fields:
             if field in form_data and isinstance(form_data[field], str) and not form_data[field].strip():
                 if field not in missing_fields: missing_fields.append(field)

        if missing_fields:
            flash(f'❌ Erro: Todos os campos obrigatórios devem ser preenchidos. Campos faltando: {", ".join(missing_fields)}', 'danger')
            return redirect(url_for('pop_form', pop_name=pop_name))

        submission_time = datetime.now()
        submission_date_str = submission_time.strftime('%Y-%m-%d')
        
        uploaded_files_paths = []
        files = [f for f in request.files.getlist('fotos[]') if f.filename]

        if len(files) < 3 or len(files) > 6:
            flash(f'❌ Erro: Você deve enviar entre 3 e 6 fotos. Você enviou {len(files)} foto(s).', 'danger')
            return redirect(url_for('pop_form', pop_name=pop_name))
        
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], pop_name, submission_date_str)
        os.makedirs(upload_path, exist_ok=True)
        
        try:
            for file in files:
                if file and allowed_file(file.filename):
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    if file_size > 10 * 1024 * 1024:
                        safe_name = secure_filename(file.filename or '')
                        raise ValueError(f'O arquivo "{safe_name}" excede o limite de 10MB.')

                    time_suffix = datetime.now().strftime('%H%M%S')
                    original_filename = secure_filename(file.filename or '')
                    filename = f"{time_suffix}_{original_filename}"
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    relative_path = os.path.relpath(file_path, app.config['UPLOAD_FOLDER']).replace('\\', '/')
                    uploaded_files_paths.append(relative_path)
            
            database.add_submission(
                pop_name=pop_name,
                inspector_name=current_user.name,
                submission_time=submission_time.strftime('%Y-%m-%d %H:%M:%S'),
                form_data=json.dumps(form_data),
                photos=json.dumps(uploaded_files_paths)
            )
            
            threading.Thread(target=check_and_alert_POP_status, args=(pop_name,)).start()
            
        except Exception as e:
            flash(f'❌ Erro ao salvar o formulário: {e}', 'danger')
            return redirect(url_for('pop_form', pop_name=pop_name))

        flash('✅ Formulário enviado com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    pop_title = pop_name.replace('-', ' ').title()
    return render_template('form.html', pop_name=pop_name, pop_title=pop_title, pops=POPS, submission=None)

def check_and_alert_POP_status(pop_name):
    """Verifica os vencimentos de um POP específico e dispara alertas de e-mail."""
    maintenance_info = database.get_maintenance_info_for_pops()
    today = datetime.now()
    
    regras = {
        'bateria': ('Banco de Baterias', 730),
        'gerador': ('Gerador', 180),
        'bateria_gerador': ('Bateria do Gerador', 180),
        'ar_condicionado': ('Ar Condicionado', 90),
        'limpeza': ('Limpeza', 30),
        'teste_bateria': ('Teste de Bateria', 30)
    }
    renewed_items = []
    
    for db_key, (display_name, dias_validade) in regras.items():
        if db_key in maintenance_info and pop_name in maintenance_info[db_key]:
            last_date = maintenance_info[db_key][pop_name]
            
            if db_key == 'bateria':
                try:
                    next_date = last_date.replace(year=last_date.year + 2)
                except ValueError:
                    next_date = last_date.replace(year=last_date.year + 2, day=28)
            else:
                next_date = last_date + timedelta(days=dias_validade)
                
            days_diff = (next_date - today).days
            
            # Avisos críticos enviamos isolados para chamar atenção
            if days_diff < 0:
                mailer.send_expiration_alert(pop_name.replace('-', ' ').title(), display_name, next_date.strftime('%d/%m/%Y'), 'Vencido')
            elif days_diff <= (dias_validade / 2.0):
                mailer.send_expiration_alert(pop_name.replace('-', ' ').title(), display_name, next_date.strftime('%d/%m/%Y'), 'Atenção (Próximo ao Vencimento)')
            else:
                # É um item renovado (verde): agrupamos no array
                renewed_items.append({"nome": display_name, "status": "OK (Renovado)"})
                
    # Dispara o email único compilado com todas as renovações
    if renewed_items:
        mailer.send_mass_maintenance_update(pop_name.replace('-', ' ').title(), renewed_items)

@app.route('/dashboard')
def dashboard():
    """Exibe o painel com as vistorias e status de manutenção."""
    filter_pop = request.args.get('pop', None)
    today_date = datetime.now().strftime('%Y-%m-%d')
    today_formatted = datetime.now().strftime('%d/%m/%Y')

    submission_rows = database.get_latest_submission_per_pop(filter_pop=filter_pop)
    
    submissions = []
    for row in submission_rows:
        sub_dict = row
        sub_dict['submission_time'] = sub_dict['submission_time'].strftime('%d/%m/%Y - %H:%M')
        submissions.append(sub_dict)

    maintenance_info = database.get_maintenance_info_for_pops()
    general_last_updates = database.get_last_update_for_each_pop()
    last_updates = {}
    today = datetime.now()
    
    pops_to_display = [filter_pop] if filter_pop else POPS

    for pop in pops_to_display:
        pop_info = {'general': general_last_updates.get(pop, 'N/A')}
        
        def get_status(next_date, validade_days):
            if next_date is None:
                return 'N/A', 'secondary'
            days_diff = (next_date - today).days
            if days_diff < 0:
                return f"Vencido ({next_date.strftime('%d/%m/%Y')})", 'danger'
            elif days_diff <= (validade_days / 2.0):
                return f"Atenção ({next_date.strftime('%d/%m/%Y')})", 'warning'
            else:
                return f"OK ({next_date.strftime('%d/%m/%Y')})", 'success'
        
        # Banco de Bateria (2 anos / 24 meses / ~730 dias)
        next_bateria = None
        if pop in maintenance_info['bateria']:
            last_change_date = maintenance_info['bateria'][pop]
            try:
                next_bateria = last_change_date.replace(year=last_change_date.year + 2)
            except ValueError:
                next_bateria = last_change_date.replace(year=last_change_date.year + 2, day=28)
            
        pop_info['bateria_status'], pop_info['bateria_color'] = get_status(next_bateria, 730)

        # Gerador (6 meses / ~180 dias)
        next_gerador = None
        if pop in maintenance_info['gerador']:
            last_date = maintenance_info['gerador'][pop]
            next_gerador = last_date + timedelta(days=180)
        pop_info['gerador_status'], pop_info['gerador_color'] = get_status(next_gerador, 180)

        # Bateria Gerador (6 meses / ~180 dias)
        next_bateria_gerador = None
        if pop in maintenance_info['bateria_gerador']:
            last_date = maintenance_info['bateria_gerador'][pop]
            next_bateria_gerador = last_date + timedelta(days=180)
        pop_info['bateria_gerador_status'], pop_info['bateria_gerador_color'] = get_status(next_bateria_gerador, 180)

        # Ar Condicionado (3 meses / ~90 dias)
        next_ar = None
        if pop in maintenance_info['ar_condicionado']:
            last_date = maintenance_info['ar_condicionado'][pop]
            next_ar = last_date + timedelta(days=90)
        pop_info['ar_condicionado_status'], pop_info['ar_condicionado_color'] = get_status(next_ar, 90)

        # Limpeza (1 Mês / 30 dias)
        next_limpeza = None
        if pop in maintenance_info['limpeza']:
            last_date = maintenance_info['limpeza'][pop]
            next_limpeza = last_date + timedelta(days=30)
        pop_info['limpeza_status'], pop_info['limpeza_color'] = get_status(next_limpeza, 30)
        
        # Teste Bateria (Teste BB / 1 mês / 30 dias)
        next_eletrica = None
        if 'teste_bateria' in maintenance_info and pop in maintenance_info['teste_bateria']:
            last_date = maintenance_info['teste_bateria'][pop]
            next_eletrica = last_date + timedelta(days=30)
            
        pop_info['eletrica_status'], pop_info['eletrica_color'] = get_status(next_eletrica, 30)


        last_updates[pop] = pop_info

    pendencias_por_pop = database.get_pendencias_abertas()
    pendencias_stats = database.get_pendencias_stats()

    # Buscar pendências já resolvidas para o histórico
    todas_resolvidas = database.get_pendencias_by_pop(status='resolvido')
    
    # Agrupar as resolvidas por POP (opcional, ou podemos mandar a lista direta, mas agrupar fica melhor no dashboard)
    pendencias_resolvidas_por_pop = {}
    for p in todas_resolvidas:
        pop = p['pop_name']
        if pop not in pendencias_resolvidas_por_pop:
            pendencias_resolvidas_por_pop[pop] = []
        pendencias_resolvidas_por_pop[pop].append(p)

    return render_template('dashboard.html', 
                         submissions=submissions, 
                         pops=POPS, 
                         today_formatted=today_formatted,
                         last_updates=last_updates,
                         pendencias_abertas=pendencias_por_pop,
                         pendencias_resolvidas=pendencias_resolvidas_por_pop,
                         pops_to_display=pops_to_display,
                         pendencias_stats=pendencias_stats,
                         now=datetime.now())

@app.route('/history')
@login_required
def submission_history():
    """Exibe o histórico completo de vistorias."""
    # Acesso restrito a Admin e Supervisor
    if not current_user.is_admin and not current_user.is_supervisor:
        flash('Acesso restrito a administradores e supervisores.', 'danger')
        return redirect(url_for('dashboard'))

    filter_pop = request.args.get('pop', None)
    submission_rows = database.get_all_submissions(filter_pop=filter_pop) # Precisa criar esta função no database.py
    
    submissions = []
    for row in submission_rows:
        sub_dict = dict(row)
        # Parse photos count
        photos = sub_dict.get('photos')
        sub_dict['photos_count'] = len(photos) if photos else 0
        submissions.append(sub_dict)

    return render_template('history.html', submissions=submissions, pops=POPS, filter_pop=filter_pop)
    


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve os arquivos de imagem que foram enviados."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/submission/<int:submission_id>/delete', methods=['POST'])
@login_required
def delete_submission_route(submission_id):
    """Exclui uma vistoria. Apenas para administradores."""
    if not current_user.is_admin:
        flash('Acesso negado: você não tem permissão para excluir.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        database.delete_submission(submission_id) # The function name in database.py should handle submission_id
        flash('Submissão excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Ocorreu um erro ao excluir a submissão: {e}', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/submission/<int:submission_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_submission(submission_id):
    """Edita uma vistoria existente. Apenas para administradores."""
    if not current_user.is_admin:
        abort(403)

    submission_row = database.get_submission(submission_id)
    if not submission_row:
        abort(404)

    submission = submission_row

    if request.method == 'POST':
        form_data = {}
        for key, values in request.form.lists():
            if key.endswith('_outro'):
                main_key = key.replace('_outro', '')
                non_empty_values = [v for v in values if v.strip()]
                if non_empty_values:
                    if main_key in form_data:
                        if not isinstance(form_data[main_key], list):
                            form_data[main_key] = [form_data[main_key]]
                        form_data[main_key].extend(non_empty_values)
                    else:
                        form_data[main_key] = non_empty_values
            elif len(values) == 1:
                form_data[key] = values[0]
            else:
                form_data[key] = values

        photos_to_delete = request.form.getlist('delete_photos')
        updated_photos = [p for p in submission['photos'] if p not in photos_to_delete]
        for photo_path in photos_to_delete:
            full_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_path.replace('/', os.sep))
            if os.path.exists(full_photo_path):
                os.remove(full_photo_path)
        new_files = [f for f in request.files.getlist('fotos') if f.filename]
        
        if len(updated_photos) + len(new_files) > 6:
            flash('❌ Erro: O número total de fotos não pode exceder 6.', 'danger')
            return redirect(url_for('edit_submission', submission_id=submission_id))

        if new_files:
            submission_time = submission['submission_time']
            submission_date_str = submission_time.strftime('%Y-%m-%d')
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], submission['pop_name'], submission_date_str)
            os.makedirs(upload_path, exist_ok=True)

            try:
                for file in new_files:
                    if file and allowed_file(file.filename):
                        file.seek(0, os.SEEK_END)
                        file_size = file.tell()
                        file.seek(0)
                        if file_size > 10 * 1024 * 1024:
                            safe_name = secure_filename(file.filename or '')
                            raise ValueError(f'O arquivo "{safe_name}" excede o limite de 10MB.')

                        time_suffix = datetime.now().strftime('%H%M%S')
                        original_filename = secure_filename(file.filename or '')
                        filename = f"{time_suffix}_{original_filename}"
                        file_path = os.path.join(upload_path, filename)
                        file.save(file_path)
                        relative_path = os.path.relpath(file_path, app.config['UPLOAD_FOLDER']).replace('\\', '/')
                        updated_photos.append(relative_path)
            except ValueError as e:
                flash(f'❌ Erro no upload: {e}', 'danger')
                return redirect(url_for('edit_submission', submission_id=submission_id))

        database.update_submission(submission_id, json.dumps(form_data), json.dumps(updated_photos))
        flash('Submissão atualizada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    pop_title = submission['pop_name'].replace('-', ' ').title()
    return render_template('form.html', pop_name=submission['pop_name'], pop_title=pop_title, pops=POPS, submission=submission)

@app.route('/users')
@login_required
def manage_users():
    """Página para gerenciar usuários."""
    if not current_user.is_admin:
        abort(403)
    users = database.get_all_users()
    return render_template('users.html', users=users, pops=POPS)

@app.route('/users/new', methods=['GET', 'POST'])
@login_required
def create_user():
    """Cria um novo usuário."""
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        role = request.form.get('role', 'user')
        is_admin = (role == 'admin')
        is_supervisor = (role == 'supervisor')

        if not username or not name or not password:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('create_user'))

        if database.get_user_by_username(username):
            flash('Este nome de usuário já existe.', 'danger')
            return redirect(url_for('create_user'))

        password_hash = generate_password_hash(password)
        database.create_user(username, password_hash, name, is_admin, is_supervisor)
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('user_form.html', action='create', pops=POPS)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edita um usuário existente."""
    if not current_user.is_admin:
        abort(403)
    
    user = database.get_user_by_id(user_id)
    if not user:
        abort(404)

    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        role = request.form.get('role', 'user')
        
        is_admin = (role == 'admin')
        is_supervisor = (role == 'supervisor')

        existing_user = database.get_user_by_username(username)
        if existing_user and existing_user['id'] != user_id:
            flash('Este nome de usuário já está em uso.', 'danger')
            return redirect(url_for('edit_user', user_id=user_id))

        database.update_user(user_id, username, name, is_admin, is_supervisor)

        if password:
            password_hash = generate_password_hash(password)
            database.update_user_password(user_id, password_hash)

        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('manage_users'))

    # Helper class to convert dict to object for template compatibility
    class UserObj:
        def __init__(self, **entries):
            self.__dict__.update(entries)
    
    user_obj = UserObj(**user) if user else None

    return render_template('user_form.html', action='edit', user=user_obj, pops=POPS)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Exclui um usuário."""
    if not current_user.is_admin or current_user.id == user_id:
        abort(403)
    database.delete_user(user_id)
    flash('Usuário excluído com sucesso.', 'success')
    return redirect(url_for('manage_users'))

@app.route('/pendencia/<int:pendencia_id>/resolver', methods=['POST'])
@login_required
def resolver_pendencia(pendencia_id):
    """Marca uma pendência como resolvida. Disponível para todos os usuários logados."""
    
    observacoes = request.form.get('observacoes', '')
    data_resolucao = datetime.now()
    
    # Busca detalhes da pendência para o e-mail antes de atualizá-la
    db = database.get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT pop_name, descricao FROM vistoria_pendencias WHERE id = %s', (pendencia_id,))
    pendencia = cursor.fetchone()
    
    try:
        database.resolve_pendencia(pendencia_id, data_resolucao, current_user.name, observacoes)
        flash(f'✅ Pendência marcada como resolvida por {current_user.name}!', 'success')
        
        # Dispara alerta de e-mail (resolução) se a pendência existir
        if pendencia:
            mailer.send_pendency_resolved(
                pop_name=pendencia['pop_name'].replace('-', ' ').title(),
                descricao_pendencia=pendencia['descricao'],
                resolved_by=current_user.name
            )
            
    except Exception as e:
        flash(f'❌ Erro ao resolver pendência: {e}', 'danger')
    
    return redirect(url_for('dashboard'))