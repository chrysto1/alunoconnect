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

        if not username or not password:
            flash('Preencha todos os campos.', 'erro')
            return render_template('login.html')

        conexao = conecta_db()
        if not conexao:
            flash('Erro ao conectar ao banco de dados.', 'erro')
            return render_template('login.html')

        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM aluno WHERE usuario = %s", (username,))
                user = cursor.fetchone()
                if user and check_password_hash(user[3], password):  # Ajuste o índice conforme a ordem das colunas
                    session.permanent = True
                    session['logged_in'] = True
                    session['username'] = user[1]  # nome do usuário
                    session['user_id'] = user[0]   # id do usuário
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

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        nome_completo = f"{firstname} {lastname}"
        
        # Armazena dados da primeira etapa
        session['cadastro_dados'] = {
            'nome': nome_completo,
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
        
        # Debug para verificar os dados recebidos
        print("Dados do formulário:", request.form)
        
        # Captura os campos do formulário
        telefone = request.form.get('phone', '')
        curso = request.form.get('curso', '')
        turma = request.form.get('turma', '')

        print(f"Telefone: {telefone}, Curso: {curso}, Turma: {turma}")

        # Verificação dos campos obrigatórios
        if not curso or not turma or not telefone:
            flash('Preencha os campos obrigatórios: telefone, curso e turma', 'erro')
            return redirect('/cadastro2')

        conecta = conecta_db()
        if not conecta:
            flash('Erro ao conectar ao banco de dados', 'erro')
            return redirect('/cadastro2')

        try:
            with conecta.cursor() as cursor:
                # Verificar se a tabela existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'aluno'
                    );
                """)
                tabela_existe = cursor.fetchone()[0]
                
                if not tabela_existe:
                    # Criar tabela conforme a estrutura correta
                    cursor.execute("""
                        CREATE TABLE aluno (
                            aluno_id serial primary key,
                            nome varchar(20) not null,
                            usuario varchar(100) unique not null,
                            data_nascimento date not null,
                            email varchar(100) unique not null,
                            senha varchar not null,
                            foto bytea,
                            telefone varchar(20) unique not null,
                            curso varchar(30) not null,
                            turma_id integer, -- removido o not null
                            CONSTRAINT chk_senha_length CHECK (char_length(senha) >= 8)
                        )
                    """)
                    conecta.commit()
                    print("Tabela aluno criada com sucesso")
                
                # Converter a data para o formato correto
                data_partes = dados['data_nascimento'].split('/')
                data_formatada = f"{data_partes[2]}-{data_partes[1]}-{data_partes[0]}"
                
                # Inserir o novo usuário
                cursor.execute("""
                    INSERT INTO aluno 
                    (nome, usuario, data_nascimento, email, senha, telefone, curso) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING aluno_id, usuario
                """, (
                    dados['nome'],
                    dados['usuario'],
                    data_formatada,
                    dados['email'],
                    dados['senha'],
                    telefone,
                    curso
                    # removido o parâmetro turma
                ))
                
                novo_usuario = cursor.fetchone()
                conecta.commit()
                print(f"Usuário cadastrado com sucesso: {novo_usuario}")

                # Configura a sessão do usuário
                session.pop('cadastro_dados', None)
                session.permanent = True
                session['logged_in'] = True
                session['username'] = dados['usuario']
                session['user_id'] = novo_usuario[0]

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
