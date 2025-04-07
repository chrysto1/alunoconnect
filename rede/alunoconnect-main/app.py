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
        conecta = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME', 'postgres'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', '123')
        )
        return conecta
    except psycopg2.Error as e:
        print(f"ERRO ao conectar ao banco de dados: {e}")
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
        username = request.form.get('email')
        password = request.form.get('senha')

        if not username or not password:
            flash('Preencha todos os campos.', 'erro')
            return render_template('login.html')

        conexao = conecta_db()
        if not conexao:
            flash('Erro ao conectar ao banco de dados.', 'erro')
            return render_template('login.html')

        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (username,))
                user = cursor.fetchone()
                if user and check_password_hash(user[2], password):
                    session.permanent = True
                    session['logged_in'] = True
                    session['username'] = user[1]
                    session['user_id'] = user[0]
                    flash('Login realizado com sucesso!', 'sucesso')
                    return redirect(url_for('homepage'))
                else:
                    flash('Usuário ou senha incorretos.', 'erro')
        except Exception as e:
            print(f"Erro na autenticação: {e}")
            flash("Erro durante a autenticação.", 'erro')
        finally:
            conexao.close()

    return render_template('login.html')

#rota principal
@sistema.route("/", methods=['GET'])
@login_required
def listar_publicacoes():
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


@sistema.route("/cadastrando", methods=["POST"])
def cadastrandousuario():
    # Obtendo os dados do formulário
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    
    # Construindo a data de nascimento
    day = request.form['day']
    month = request.form['month']
    year = request.form['year']
    birthdate = f"{day}/{month}/{year}"

    # Capturando o gênero
    gender = request.form.get('gender', None)

    # Agora, conectando ao banco de dados
    conecta = conecta_db()
    if not conecta:
        return jsonify({'erro': 'Erro ao conectar ao banco de dados.'}), 500

    try:
        cursor = conecta.cursor()
        # Corrigindo a query SQL: adicionando vírgulas entre os placeholders
        cursor.execute("INSERT INTO usuario (firstname, lastname, email, username, password, birthdate, day, month, year, gender) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                       (firstname, lastname, email, username, password, birthdate, day, month, year, gender))
        conecta.commit()
        cursor.close()
    except Exception as e:
        print(f"Erro ao inserir no banco: {e}")
        return jsonify({'erro': 'Erro ao salvar a postagem no banco de dados.'}), 500
    finally:
        conecta.close()

    return render_template('cadastro2.html')


@sistema.route("/perfil/<int:user_id>")
@login_required
def perfil(user_id):
    conexao = conecta_db()
    if not conexao:
        return "Erro ao conectar ao banco de dados.", 500

    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id, texto, criado_em 
            FROM postagens 
            WHERE user_id = %s
        """, (user_id,))
        postagens = cursor.fetchall()
        cursor.close()
        return render_template('perfil.html', postagens=postagens)
    finally:
        conexao.close()


#rota para postar

@sistema.route("/publicacao_texto", methods=['POST'])
@login_required
def publicacao_texto():
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
            FROM usuarios
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


    

if __name__ == "__main__":
    sistema.run(debug=True, port=8085, host='127.0.0.1')
