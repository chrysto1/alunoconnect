from flask import Flask, render_template, request, make_response, redirect, url_for, flash, session, jsonify
import psycopg2
import math
import os
import base64
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

# Configuração inicial
sistema = Flask(__name__)
sistema.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback-secret-key-aula2025')
sistema.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Função de conexão com o banco de dados
def conecta_db():
    try:
        print("Tentando conectar ao banco de dados...")
        conecta = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME', 'alunoconnect'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', '1234')
        )
        print("Conexão estabelecida com sucesso!")
        return conecta
    except psycopg2.Error as e:
        print(f"ERRO ao conectar ao banco de dados:")
        print(f"Detalhes do erro: {e}")
        print(f"Configurações utilizadas:")
        print(f"Host: {os.environ.get('DB_HOST', 'localhost')}")
        print(f"Database: {os.environ.get('DB_NAME', 'alunoconnect')}")
        print(f"User: {os.environ.get('DB_USER', 'postgres')}")
        return None

# Proteção de rota
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Por favor, faça login para acessar esta página.', 'erro')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@sistema.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('usuario')
        password = request.form.get('senha')
        
        print(f"Tentativa de login - Usuário: {username}")  # Debug 1

        if not username or not password:
            flash('Preencha todos os campos.', 'erro')
            return render_template('login.html')

        conexao = conecta_db()
        if not conexao:
            print("Falha na conexão com o banco")  # Debug 2
            flash('Erro ao conectar ao banco de dados.', 'erro')
            return render_template('login.html')

        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM aluno WHERE usuario = %s", (username,))
                user = cursor.fetchone()
                print(f"Resultado da consulta: {user}")  # Debug 3
                
                if user:
                    print(f"Senha hash do banco: {user[6]}")  # Debug 4
                    senha_valida = check_password_hash(user[6], password)
                    print(f"Resultado da validação da senha: {senha_valida}")  # Debug 5
                
                if user and check_password_hash(user[6], password):  # índice 6 é a senha
                    session.permanent = True
                    session['logged_in'] = True
                    session['nome'] = user[1]      # nome
                    session['curso'] = user[9]     # curso (índice 9 - último campo)
                    session['user_id'] = user[0]   # id
                    flash('Login realizado com sucesso!', 'sucesso')
                    return redirect(url_for('homepage'))
                else:
                    print("Usuário não encontrado ou senha incorreta")  # Debug 7
                    flash('Usuário ou senha incorretos.', 'erro')
        except Exception as e:
            print(f"Erro detalhado na autenticação: {str(e)}")  # Debug 8
            flash("Erro durante a autenticação.", 'erro')
        finally:
            conexao.close()

    return render_template('login.html')

#rota principal
@sistema.route("/", methods=['GET'])
@login_required
def homepage():
    try:
        # Conecta ao banco de dados
        conexao = conecta_db()
        if not conexao:
            return "Erro ao conectar ao banco de dados", 500

        try:
            with conexao.cursor() as cursor:
                # Busca todas as publicações
                cursor.execute("SELECT * FROM postagens ")
                publicacoes = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar publicações: {e}")
            return "Erro ao buscar publicações", 500
        finally:
            conexao.close()

        # Renderiza o template com as publicações
        return render_template("home.html", publicacoes=publicacoes)

    except Exception as e:
        print(f"Erro inesperado: {e}")
        return "Erro inesperado no servidor", 500
    


#rota para sair do sistema desconectando o e-mail 
@sistema.route("/logout")
@login_required
def logout():
    session.clear()
    flash('Você foi deslogado.', 'success')
    return redirect(url_for('login'))

@sistema.route("/redefinirSenha")
def redefinir():
    return render_template("redifinirsenha.html")

@sistema.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@sistema.route("/developers")
def developers():
    return render_template("developers.html")

@sistema.route("/cadastro2")
def cadastro2():
    if 'cadastro_dados' not in session:
        flash('Por favor, preencha primeiro a etapa 1 do cadastro', 'erro')
        return redirect('/cadastro')
    return render_template("cadastro2.html")

@sistema.route("/cadastrando", methods=["POST"])
def cadastrandousuario():
    try:
        # Validação dos dados da primeira página
        required_fields = ['firstname', 'lastname', 'username', 'email', 'password', 'day', 'month', 'year']
        if not all(request.form.get(field) for field in required_fields):
            flash('Preencha todos os campos obrigatórios', 'erro')
            return redirect('/cadastro')

        # Store first name and last name separately
        session['cadastro_dados'] = {
            'nome': request.form['firstname'],
            'sobrenome': request.form['lastname'],
            'usuario': request.form['username'],
            'email': request.form['email'],
            'senha': generate_password_hash(request.form['password']),
            'data_nascimento': f"{request.form['day']}/{request.form['month']}/{request.form['year']}"
        }
        
        return redirect('/cadastro2')
    except Exception as e:
        print(f"Erro ao processar primeira etapa: {e}")
        flash('Erro ao processar dados do cadastro', 'erro')
        return redirect('/cadastro')

@sistema.route("/finalizar_cadastro", methods=["POST"])
def finalizar_cadastro():
    if 'cadastro_dados' not in session:
        flash('Por favor, complete a primeira etapa do cadastro', 'erro')
        return redirect('/cadastro')

    try:
        dados = session['cadastro_dados']
        
        # Get form data
        telefone = request.form.get('phone', '')
        curso = request.form.get('curso', '')

        # Updated validation (removed turma check)
        if not curso or not telefone:
            flash('Preencha os campos obrigatórios: telefone e curso', 'erro')
            return redirect('/cadastro2')

        conecta = conecta_db()
        if not conecta:
            flash('Erro ao conectar ao banco de dados', 'erro')
            return redirect('/cadastro2')

        try:
            with conecta.cursor() as cursor:
                # First, ensure the table exists with the correct structure
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS aluno (
                        aluno_id SERIAL PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        sobrenome VARCHAR(100) NOT NULL,
                        usuario VARCHAR(100) UNIQUE NOT NULL,
                        data_nascimento DATE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        senha VARCHAR(255) NOT NULL,
                        telefone VARCHAR(20) NOT NULL,
                        curso VARCHAR(100) NOT NULL
                    )
                """)
                conecta.commit()

                # Convert date to correct format
                data_partes = dados['data_nascimento'].split('/')
                data_formatada = f"{data_partes[2]}-{data_partes[1]}-{data_partes[0]}"
                
                # Insert new user
                cursor.execute("""
                    INSERT INTO aluno 
                    (nome, sobrenome, usuario, data_nascimento, email, senha, telefone, curso) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING aluno_id, usuario
                """, (
                    dados['nome'],
                    dados['sobrenome'],
                    dados['usuario'],
                    data_formatada,
                    dados['email'],
                    dados['senha'],
                    telefone,
                    curso
                ))
                
                novo_usuario = cursor.fetchone()
                conecta.commit()

                # Configure user session
                session.pop('cadastro_dados', None)
                session.permanent = True
                session['logged_in'] = True
                session['nome'] = dados['nome']      # nome
                session['curso'] = curso             # curso
                session['user_id'] = novo_usuario[0] # id do usuário

                flash('Cadastro realizado com sucesso!', 'sucesso')
                return redirect(url_for('homepage'))

        except Exception as e:
            print(f"Erro detalhado no banco de dados: {e}")
            flash(f'Erro ao salvar os dados: {str(e)}', 'erro')
            conecta.rollback()  # Added rollback on error
            return redirect('/cadastro2')
        finally:
            conecta.close()

    except Exception as e:
        print(f"Erro ao finalizar cadastro: {e}")
        flash(f'Erro ao processar o cadastro: {str(e)}', 'erro')
        return redirect('/cadastro2')


@sistema.route("/perfil/<int:user_id>")
@login_required
def perfil(user_id):
    conexao = conecta_db()
    if not conexao:
        return "Erro ao conectar ao banco de dados.", 500

    try:
        with conexao.cursor() as cursor:
            # Buscar apenas informações do usuário
            cursor.execute("""
                SELECT aluno_id, nome, sobrenome, curso 
                FROM aluno 
                WHERE aluno_id = %s
            """, (user_id,))
            user_info = cursor.fetchone()

            if not user_info:
                return "Usuário não encontrado", 404

            return render_template('perfil.html', user=user_info)
    except Exception as e:
        print(f"Erro ao carregar perfil: {e}")
        return "Erro ao carregar perfil", 500
    finally:
        conexao.close()


#rota para postar

@sistema.route('/processar_dados', methods=['POST'])
def processar_dados():
    try:
        dados = request.get_json()
        conteudo = dados.get("conteudo")

        # Simples verificação adicional para maior segurança
        if "<script>" in conteudo:
            return jsonify({"error": "Conteúdo inválido!"}), 400

        # Salvando no banco de dados
        conexao = conecta_db()
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO postagens (texto) VALUES (%s)", (conteudo,))
        conexao.commit()  # Confirmação
        cursor.close()


        return jsonify({"message": "Publicado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#@sistema.route("/publicacao_texto", methods=['POST'])
#@login_required
#def publicacao_texto():
    try:
        # Obtém os dados do formulário enviado
        texto = request.form.get('conteudo')

        # Valida se o texto não está vazio
        if not texto or not texto.strip():
            return render_template('erro.html', mensagem='Texto não pode estar vazio ou apenas com espaços.')

        # Valida o tamanho do texto (por exemplo, até 500 caracteres)
        if len(texto) > 500:
            return render_template('erro.html', mensagem='Texto excede o limite permitido de caracteres.')

        # Salva os dados no banco de dados
        conexao = conecta_db()
        if not conexao:
            return render_template('erro.html', mensagem='Erro ao conectar ao banco de dados.')

        
        with conexao.cursor() as cursor:
            cursor.execute("INSERT INTO postagens (texto) VALUES (%s)", (texto,))
            conexao.commit()
            conexao.close()
        # Redireciona para uma página de sucesso
        return render_template('home.html', mensagem='Postagem salva com sucesso!')
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return render_template('erro.html', mensagem='Erro inesperado no servidor.')

#rota para filtrar os usuarios que estão no

@sistema.route('/pesquisar', methods=['GET'])
def pesquisar():
    nome = request.args.get('nome', '')
    conexao = conecta_db()  # Sua função de conexão ao banco
    if not conexao:
        return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT nome
            FROM aluno
            WHERE nome LIKE %s
        """, (f"%{nome}%",))  # Busca parcial
        usuarios = cursor.fetchall()
        cursor.close()
        conexao.close()

        # Transformar os resultados em uma lista de dicionários
        usuarios_filtrados = [{"nome": i[1]} for i in usuarios]

        return jsonify(usuarios_filtrados)
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        return jsonify({"erro": "Erro ao buscar usuários"}), 500


    

@sistema.route('/terms')
def terms():
    return render_template('terms.html')

if __name__ == "__main__":
    sistema.run(debug=True, port=8085, host='127.0.0.1')
