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
            database=os.environ.get('DB_NAME', 'alunoconnect'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', '1234')
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
        username = request.form.get('usuario')
        password = request.form.get('senha')

        if not username or not password:
            flash('Preencha todos os campos.', 'erro')
            return render_template('login.html')

        conexao = conecta_db()
        if not conexao:
            flash('Erro ao conectar ao banco de dados.', 'erro')
            return render_template('login.html')

        try:
            # Na função login
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM aluno WHERE usuario = %s", (username,))
                user = cursor.fetchone()
                if user and check_password_hash(user[5], password):
                    session.permanent = True
                    session['logged_in'] = True
                    session['username'] = user[1]  # nome completo
                    session['user_id'] = user[0]
                    session['curso'] = user[8]
                    flash('Login realizado com sucesso!', 'sucesso')
                    return redirect(url_for('homepage'))

# Na função finalizar_cadastro
                # Configura a sessão do usuário
                session.pop('cadastro_dados', None)
                session.permanent = True
                session['logged_in'] = True
                session['username'] = dados['nome']  # nome completo
                session['user_id'] = novo_usuario[0]
                session['curso'] = curso
                    
                flash('Cadastro realizado com sucesso!', 'sucesso')
                return redirect(url_for('homepage'))

        except Exception as e:
            print(f"Erro detalhado no banco de dados: {e}")
            flash(f'Erro ao salvar os dados: {str(e)}', 'erro')
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
