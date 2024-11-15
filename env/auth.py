from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import Endereco, Curso, Disciplina, Aluno, Professor, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type') 
        user_name = request.form.get('user')
        password = request.form.get('password')

        if(user_type == "aluno"):
            user = Aluno.query.filter_by(usuario=user_name).first()
        else:
            user = Professor.query.filter_by(usuario=user_name).first()

        if user:
            if check_password_hash(user.senha, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                session["user_type"] = user_type
                return redirect(url_for('views.home'))
            else:
                flash('Usuário ou senha incorretos. Tente novamente', category='error')
        else:
            flash('Usuário ou senha incorretos. Tente novamente', category='error')
    return render_template("login.html",  user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('views.home'))

@auth.route('/signup/professor', methods=['GET', 'POST'])
def sign_up_professor():
    disciplines = Disciplina.query.all()
    if request.method == "POST":
        user = request.form.get("user")
        name = request.form.get("name")
        phone = request.form.get("phone")

        selected_disciplines = request.form.getlist("disciplines")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if len(user) < 4:
            flash("Usuário precisa ser maior que 4 caracteres.", category = "error")
        elif len(name) < 2:
            flash("Nome precisa ser maior que 1 caracter.", category = "error")
        elif password1 != password2:
            flash("As senhas não são iguais.", category = "error")
        elif len(password1) < 7:
            flash("Senha precisa ter pelo menos 7 caracteres.", category = "error")
        # elif selected_disciplines:
        #     flash("Alguma disciplina precisa ser selecionada, category = "error")
        else:
            selected_disciplines = [int(discipline_id) for discipline_id in selected_disciplines]
            disciplinas = Disciplina.query.filter(Disciplina.id.in_(selected_disciplines)).all()

            new_user = Professor(
                usuario=user,
                nome=name,
                telefone=phone,
                senha=generate_password_hash(password1, method='pbkdf2:sha256')
            )
            
            # Adicionar as disciplinas selecionadas
            new_user.disciplina_ministrada.extend(disciplinas)

            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user_type="professor", disciplines=disciplines, user=current_user)

@auth.route('/signup/aluno', methods=['GET', 'POST'])
def sign_up_aluno():
    cursos = Curso.query.all()

    cursos_data = {
        curso.id: [{"nome": disciplina.nome, "carga_horaria": disciplina.carga_horaria} for disciplina in curso.disciplinas]
        for curso in cursos
    }

    if request.method == "POST":
        user = request.form.get("user")
        name = request.form.get("name")
        course_id = request.form.get("course")
        cpf = request.form.get("cpf")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        rua = request.form.get("rua")
        numero = request.form.get("numero")
        bairro = request.form.get("bairro")
        cep = request.form.get("cep")
        complemento = request.form.get("complemento")

        if len(user) < 4:
            flash("Usuário precisa ser maior que 4 caracteres.", category = "error")
        elif len(name) < 2:
            flash("Nome precisa ser maior que 1 caracter.", category = "error")
        elif password1 != password2:
            flash("As senhas não são iguais.", category = "error")
        elif len(password1) < 7:
            flash("Senha precisa ter pelo menos 7 caracteres.", category = "error")
        else:
            novo_endereco = Endereco(
                rua=rua,
                numero=numero,
                bairro=bairro,
                cep=cep,
                complemento = complemento
            )

            novo_aluno = Aluno(
                usuario=user,
                nome=name,
                cpf=cpf,
                curso_id=course_id,
                senha=generate_password_hash(password1, method='pbkdf2:sha256'),
                endereco=novo_endereco  
            )

            db.session.add(novo_endereco)
            db.session.add(novo_aluno)
            db.session.commit()

            login_user(novo_aluno, remember=True)
            flash("Conta criada com sucesso!", category="success")
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user_type="aluno", cursos=cursos, cursos_data=cursos_data, user=current_user)

@auth.route('/cursos/cadastro', methods=['GET','POST'])
@login_required
def new_course():
    disciplinas = Disciplina.query.all()
    disciplinas_data = [
        {"id": d.id, "nome": d.nome, "carga_horaria": d.carga_horaria}
        for d in disciplinas
    ]
    if request.method == "POST":
        nome = request.form.get('nome')
        disciplinas_ids = request.form.getlist('disciplinas')

        if not nome or not disciplinas_ids:
            flash("O nome do curso/disciplina são obrigatórios.", "error")
            return redirect(url_for("auth.new_course"))

        novo_curso = Curso(nome=nome)

        # Associa as disciplinas selecionadas ao curso
        for disciplina_id in disciplinas_ids:
            disciplina = Disciplina.query.get(disciplina_id)
            if disciplina:
                novo_curso.disciplinas.append(disciplina)

        try:
            # Salva o curso no banco de dados
            db.session.add(novo_curso)
            db.session.commit()
            flash("Curso adicionado com sucesso!", "success")
            return redirect(url_for("views.cursos"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao adicionar o curso: {str(e)}", "error")

    return render_template("add_course.html", user = current_user, disciplinas_data=disciplinas_data)

@auth.route('/disciplinas/cadastro', methods=['GET','POST'])
@login_required
def new_discipline():
    if request.method == "POST":
        nome = request.form.get("nome")
        carga_horaria = request.form.get("carga_horaria")

        if not nome or not carga_horaria:
            flash("Todos os campos são obrigatórios.", "error")
            return redirect(url_for("auth.new_discipline"))

        nova_disciplina = Disciplina(nome=nome, carga_horaria=int(carga_horaria))
        
        try:
            db.session.add(nova_disciplina)
            db.session.commit()
            flash("Disciplina cadastrada com sucesso.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao cadastrar disciplina: {str(e)}", "error")

        return redirect(url_for("views.disciplinas"))

    return render_template("add_discipline.html", user=current_user)

@auth.route('/edit/<string:tipo>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit(tipo, item_id):
    cursos = Curso.query.all()
    disciplines = Disciplina.query.all()
    cursos_data = {
        curso.id: [
            {
                "id": disciplina.id,
                "nome": disciplina.nome,
                "carga_horaria": disciplina.carga_horaria,
                "associado": disciplina in curso.disciplinas  # True se a disciplina já fizer parte do curso
            }
            for disciplina in Disciplina.query.all()  # Todas as disciplinas
        ]
        for curso in cursos
    }
    if tipo == 'aluno':
        item = Aluno.query.get_or_404(item_id)
    elif tipo == 'professor':
        item = Professor.query.get_or_404(item_id)
    elif tipo == 'curso':
        item = Curso.query.get_or_404(item_id)
    elif tipo == "disciplina":
        item = Disciplina.query.get_or_404(item_id)
    else:
        flash("Tipo de item inválido.", 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        if tipo == "aluno":
            item.nome = request.form.get('nome')
            item.cpf = request.form.get('cpf')
            item.usuario = request.form.get('user')
            item.curso_id = request.form.get('course')

            if item.endereco:
                item.endereco.rua = request.form.get('rua')
                item.endereco.numero = request.form.get('numero')
                item.endereco.bairro = request.form.get('bairro')
                item.endereco.cep = request.form.get('cep')
                item.endereco.complemento = request.form.get('complemento')
            else:
                item.endereco = Endereco(
                    rua=request.form.get('rua'),
                    numero=request.form.get('numero'),
                    bairro=request.form.get('bairro'),
                    cep=request.form.get('cep'),
                    complemento=request.form.get('complemento')
                )

        elif tipo == "curso":
            item.nome = request.form.get('nome')

            disciplinas_ids = request.form.getlist('disciplinas')
            print(f"Disciplinas selecionadas: {disciplinas_ids}")
            
            item.disciplinas = []
            
            for disciplina_id in disciplinas_ids:
                disciplina = Disciplina.query.get(disciplina_id)
                if disciplina:
                    item.disciplinas.append(disciplina)
        
        elif tipo == "disciplina":
            item.nome = request.form.get("nome")
            item.carga_horaria = int(request.form.get("carga_horaria"))

        elif tipo == "professor":
            item.nome = request.form.get('nome')
            item.usuario = request.form.get('user')
            item.telefone = request.form.get('phone')
            
            disciplinas_ids = request.form.getlist('disciplines')
            item.disciplina_ministrada = []
            
            for disciplina_id in disciplinas_ids:
                disciplina = Disciplina.query.get(disciplina_id)
                if disciplina:
                    item.disciplina_ministrada.append(disciplina)
        try:
            db.session.commit()
            flash(f'{tipo} atualizado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o {tipo}: {str(e)}', 'error')
        finally:
            return redirect(url_for(f'views.{tipo}s'))
    
    return render_template('edit.html', item=item, tipo=tipo, user=current_user, cursos_data=cursos_data, cursos=cursos, disciplines=disciplines)

@auth.route('/delete/<string:tipo>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete(tipo, item_id):
    user_type = session.get('user_type')
    if tipo == "aluno":
        item = Aluno.query.get_or_404(item_id)
    elif tipo == "professor":
        item = Professor.query.get_or_404(item_id)
    elif tipo == "curso":
        item = Curso.query.get_or_404(item_id)
    elif tipo == "disciplina":
        item = Disciplina.query.get_or_404(item_id)
    else:
        flash("Tipo de item inválido.", 'error')
        return redirect(url_for('views.home'))
    
    # Verificação de dependências antes da exclusão
    if tipo == "curso" and item.alunos:
        flash("Não é possível excluir o curso, pois há alunos matriculados.", 'error')
        return redirect(url_for('views.cursos'))
    
    if tipo == "disciplina" and (item.cursos or item.professores):
        flash("Não é possível excluir a disciplina, pois ela está vinculada a cursos.", 'error')
        return redirect(url_for('views.disciplinas'))
    
    if tipo == "aluno" and user_type == "aluno" and item.id == current_user.id:
        flash("Você está prestes a excluir o próprio usuário. Isso irá deslogá-lo do sistema.", 'warning')
        confirmation = request.args.get('confirm')
        
        if confirmation != 'yes':
            return redirect(url_for('views.confirm_delete', user = current_user, tipo=tipo, item_id=item_id))
    
    elif tipo == "professor" and user_type == "professor" and item.id == current_user.id:
        flash("Você está prestes a excluir o próprio usuário. Isso irá deslogá-lo do sistema.", 'warning')
        confirmation = request.args.get('confirm')
        
        if confirmation != 'yes':
            return redirect(url_for('auth.confirm_delete', user = current_user, tipo=tipo, item_id=item_id))
    
    try:
        db.session.delete(item)
        db.session.commit()
        flash(f"{tipo.capitalize()} excluído com sucesso.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir {tipo}: {str(e)}", 'error')
    
    # Redireciona para a lista correta após a exclusão
    return redirect(url_for(f'views.{tipo}s'))

@auth.route('/confirm_delete/<string:tipo>/<int:item_id>')
@login_required
def confirm_delete(tipo, item_id):
    return render_template("confirm_delete.html", user = current_user, tipo=tipo, item_id=item_id)
