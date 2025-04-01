from flask import Flask, render_template, request, make_response, redirect, url_for, flash, session
import psycopg2
import math
from PIL import Image #biblioteca para trabalhar com imagens


#biblioteca para o login
from flask_wtf.csrf import CSRFProtect
from functools import wraps  #decoretion , é o que vai fazer eu poder acessar só passando pelo login
from werkzeug.security import generate_password_hash, check_password_hash #gerar e verificar a senha , usando a função hash
from datetime import timedelta
from dotenv import load_dotenv 
load_dotenv()

#aqui é a área importante para cadastro de fotos/imagens
import os
import base64
from io import BytesIO
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'  # Pasta para salvar imagens no servidor
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Cria a pasta se ela não existir
#LIBs para gerar o relatório em pdf (adicione o MAKE_RESPOSE acima)
from flask_sqlalchemy import SQLAlchemy
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph


sistema = Flask(__name__)

#configurações de seguraça 
sistema.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback-secret-key-aula2025')
sistema.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) #definindo a duração do sistema qua ficará ativo
csrf = CSRFProtect(sistema)

def conecta_db():
    try:
#aqui fica a parte de conexão com o postgree usando proteção
#usu as váriaveis de ambiente salvas no bloco de notas 
        conecta = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME','postgres'),
            user=os.environ.get('DB_USAR', 'postgres'),
            password=os.environ.get('DB_PASSWORD', '123')
        )
        return conecta
    except psycopg2.Error as e:
        print(f"ERRO ao conectar ao banco de dados: {e}")


#proteção das rotas
def login_requirid(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Por favor, faça login para acessar está pagina','erro')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



@sistema.route("/login")
@login_requirid
def requisicao_login():
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('senha')

        if not username or not password:
            flash('preecha todos os campos')
            return render_template('login.html')
        
        conexao = conecta_db()

        if not conexao:
            flash('Erro ao conectao ao banco de dados', 'Erro')
            return render_template('login.html')
        
        try:

            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (username,))
                user = cursor.fetchone()

                if user and (user[2], password):
                    session.permanet = True
                    session['logger_in'] = True
                    session['username'] = user[1]
                    session['user_id'] = user[0]
                    flash['login realizado com sucesso','sucess']
                    return redirect(url_for('homepage'))
                else:
                    print(user)
                    flash('usuario ou senha incorretos','Erro')
        except Exception as e:
            print(f"Erro na autenticação {e}")
            flash("Erro durante a autentiucação")

        finally:
            if conexao:
                conexao.close()

    return render_template('login.html')

@sistema.route("/")
def homepage():
    return render_template('home.html')



# Rota inicial
#@sistema.route("/")
#def homepage():
    cursor = conecta_db().cursor()
    cursor.execute("""SELECT * FROM postagens""")
    cursor.connection.commit()
    destaque = cursor.fetchall()
    cursor.close()

    # Convertendo os dados binários para Base64
    destaque_formatado = []
    for item in destaque:
        texto = item[1]
        imagem_binaria = item[2]

        # Verifique se a imagem não é None antes de converter
        if imagem_binaria:
            imagem_base64 = base64.b64encode(imagem_binaria).decode('utf-8')  # Converte para Base64
        else:
            imagem_base64 = None  # Define como None para imagens ausentes

        destaque_formatado.append((item[0], texto, imagem_base64))

    return render_template('index.html', page=1, destaque=destaque_formatado)


#rota para gerar o PDF
@sistema.route("/baixarPDF")
def baixarPDF():
    try:
        cursor = conecta_db().cursor()
        cursor.execute("""SELECT * FROM produto_destaque""")
        gerar_pdf = cursor.fetchall()
        cursor.close()
    except Exception as e:
        return f"Erro ao consultar banco de dados: {str(e)}", 500

    guardarPDFtemporariamente = BytesIO()
    tamanho_da_pagina = (900, 600)
    p = canvas.Canvas(guardarPDFtemporariamente, pagesize=tamanho_da_pagina)
    width, height = tamanho_da_pagina

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="titlestyles",
        fontSize=18,
        textColor=colors.darkblue,
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        underline=True
    )

    title = Paragraph('Relatório de Produtos', title_style)
    title.wrapOn(p, width - 200, height)
    title.drawOn(p, 50, height - 50)

    dados_da_tabela = [('id', 'medicamento', 'quantidade', 'preco', 'imagem', 'criado_em')] + list(gerar_pdf)
    coluna_largura = [30, 80, 80, 80, 80, 160]
    tabela = Table(dados_da_tabela, coluna_largura)

    tabela_estilos = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    tabela.setStyle(tabela_estilos)
    tabela.wrapOn(p, width - 300, height - 200)
    tabela.drawOn(p, 50, height - 300)

    p.showPage()
    p.save()

    guardarPDFtemporariamente.seek(0)
    response = make_response(guardarPDFtemporariamente.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio.pdf'

    return response

      
#Rota da paginação
@sistema.route("/paginacao", methods=['GET', 'POST'] )
def paginacao():
    page = request.args.get('page', 1, type=int)
    quantidade = 5

    conexao = conecta_db()
    cursor = conexao.cursor()

    #Aqui ele vai contar a quantidade de registros
    cursor.execute('SELECT count(*) FROM produto')
    total_items = cursor.fetchone()[0]

    #Calcular o número total de páginas
    total_pages = math.ceil(total_items / quantidade)

    #Calcular a saída da consulta
    offset = (page - 1) * quantidade

    cursor.execute('''SELECT * FROM produto ORDER BY medicamento LIMIT %s OFFSET %s''', (quantidade, offset))

    clientes = cursor.fetchall()
    cursor.close()
    conexao.close()


    #return render_template('grid_completo.html', clientes=clientes_lista, page=page, total_pages=total_pages)
    return render_template('index2.html', clientes=clientes, page=page, total_pages=total_pages)

@sistema.route("/cadastro", methods=['POST'])
def cadastro():          
    texto = request.form.get('texto')

    
    # Verificação dos campos obrigatórios
    if not texto:
        return "Campos obrigatórios estão faltando", 400
    
    # Inserindo os dados no banco de dados (salva apenas o caminho da imagem)
    cursor = conecta_db().cursor()
    cursor.execute("""
        INSERT INTO postagens (texto) 
        VALUES (%s)
    """, (texto,))
    cursor.connection.commit()
    cursor.close()

    return render_template('index.html')
        




@sistema.route("/cadastro_imagem", methods=['GET', 'POST'])
def cadastro_foto():
    if request.method == 'POST':
        foto = request.files['foto']

        if foto:
            #Lê a imagem como dados binários
            foto_binaria = foto.read()

            conexao = conecta_db()
            cursor = conexao.cursor()
            cursor.execute("INSERT INTO postagens ( foto) VALUES (%s)", (foto_binaria))
            conexao.commit()
            cursor.close()
            conexao.close()

        return redirect(url_for('cadastro_foto'))
   
    return render_template('index.html')


if __name__ == "__main__":
    sistema.run(debug=True, port=8085, host='127.0.0.1')
