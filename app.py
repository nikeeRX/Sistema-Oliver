import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
# Chave de segurança para as sessões (no Railway, crie a variável SECRET_KEY)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_secreta_local_para_testes')

# --- CONFIGURAÇÃO DO BANCO DE DADOS RAIZ ---
def get_db_connection():
    # O Railway fornece a DATABASE_URL automaticamente nas variáveis de ambiente
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

# --- INICIALIZAÇÃO AUTOMÁTICA DO BANCO ---
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Cria a tabela de Usuários (se não existir)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        );
    ''')
    
    # 2. Cria a tabela de Produtos/Decants (se não existir)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            descricao TEXT,
            preco NUMERIC(10,2) NOT NULL,
            volume_ml INTEGER NOT NULL,
            estoque INTEGER DEFAULT 0,
            imagem_url VARCHAR(255)
        );
    ''')
    
    # 3. Insere o produto de teste apenas se a tabela estiver vazia
    cur.execute('SELECT COUNT(*) FROM produtos;')
    if cur.fetchone()[0] == 0:
        cur.execute('''
            INSERT INTO produtos (nome, descricao, preco, volume_ml, estoque, imagem_url) 
            VALUES ('Oliva Imperial', 'Notas amadeiradas com especiarias raras.', 189.90, 10, 50, 'perfume.jpg');
        ''')
    
    conn.commit()
    cur.close()
    conn.close()

# Executa a verificação e criação das tabelas assim que o app iniciar
try:
    init_db()
    print("Banco de dados verificado/inicializado com sucesso!")
except Exception as e:
    print(f"Aguardando conexão com o banco... {e}")

# --- DECORATORS PARA PROTEGER ROTAS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, faça login para acessar.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or not session.get('is_admin'):
            flash('Acesso restrito apenas para administradores.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# ROTAS PÚBLICAS (VITRINE E CARRINHO)
# ==========================================

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    # Busca apenas produtos com estoque positivo
    cur.execute('SELECT * FROM produtos WHERE estoque > 0 ORDER BY id DESC;')
    produtos = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('index.html', produtos=produtos)

@app.route('/carrinho')
def carrinho():
    carrinho_itens = session.get('carrinho', {})
    produtos_carrinho = []
    total = 0.0

    if carrinho_itens:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        for id_produto, qtd in carrinho_itens.items():
            cur.execute('SELECT id, nome, preco, imagem_url, volume_ml FROM produtos WHERE id = %s;', (id_produto,))
            produto = cur.fetchone()
            if produto:
                produto['quantidade'] = qtd
                produto['subtotal'] = float(produto['preco']) * qtd
                total += produto['subtotal']
                produtos_carrinho.append(produto)
                
        cur.close()
        conn.close()

    return render_template('carrinho.html', produtos=produtos_carrinho, total=total)

@app.route('/carrinho/adicionar/<int:id_produto>', methods=['POST'])
def adicionar_carrinho(id_produto):
    if 'carrinho' not in session:
        session['carrinho'] = {}
    
    carrinho = session['carrinho']
    id_str = str(id_produto)
    
    carrinho[id_str] = carrinho.get(id_str, 0) + 1
    session['carrinho'] = carrinho
    session.modified = True
    
    flash("Decant adicionado ao carrinho de compras!", "success")
    return redirect(url_for('index'))

@app.route('/carrinho/limpar')
def limpar_carrinho():
    session.pop('carrinho', None)
    flash("Carrinho esvaziado.", "success")
    return redirect(url_for('carrinho'))

# ==========================================
# SISTEMA DE LOGIN (CLIENTE E ADM)
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM usuarios WHERE email = %s;', (email,))
        usuario = cur.fetchone()
        cur.close()
        conn.close()
        
        if usuario and check_password_hash(usuario['senha'], senha):
            session['usuario_id'] = usuario['id']
            session['nome'] = usuario['nome']
            session['is_admin'] = usuario['is_admin']
            
            if usuario['is_admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('meus_pedidos'))
        else:
            flash('E-mail ou senha incorretos.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ==========================================
# ÁREA DO CLIENTE
# ==========================================

@app.route('/meus-pedidos')
@login_required
def meus_pedidos():
    return render_template('pedidos.html')

# ==========================================
# ÁREA ADMINISTRATIVA (BACKOFFICE)
# ==========================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM produtos ORDER BY id DESC;')
    produtos = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('admin.html', produtos=produtos)

@app.route('/admin/produto/novo', methods=['POST'])
@admin_required
def admin_novo_produto():
    nome = request.form['nome']
    descricao = request.form.get('descricao', '')
    preco = request.form['preco']
    volume_ml = request.form['volume_ml']
    estoque = request.form['estoque']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO produtos (nome, descricao, preco, volume_ml, estoque)
        VALUES (%s, %s, %s, %s, %s);
    ''', (nome, descricao, preco, volume_ml, estoque))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Novo decant catalogado com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    # No Railway, a porta é injetada por variável de ambiente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
