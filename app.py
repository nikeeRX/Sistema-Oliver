import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jinja2

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_secreta_local_para_testes')

# ==========================================
# 1. FRONTEND RAIZ EMBUTIDO (HTML + CSS)
# ==========================================
# O Flask vai ler todas as telas direto desse dicionário na memória

TEMPLATES = {
    'base.html': '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OLIVA - Fragrância em Decants</title>
        <style>
            /* Reset e Tipografia */
            body, h1, h2, h3, p, ul, form { margin: 0; padding: 0; box-sizing: border-box; }
            body { background-color: #fdfbf7; color: #2c2621; font-family: 'Helvetica Neue', Arial, sans-serif; }
            
            /* Navbar */
            .navbar { background-color: #ffffff; border-bottom: 1px solid #dfd5c6; padding: 15px 0; }
            .nav-container { max-width: 1100px; margin: 0 auto; padding: 0 20px; clear: both; }
            .logo-text { font-family: 'Georgia', serif; font-size: 20pt; font-weight: bold; color: #2c2621; text-decoration: none; letter-spacing: 3px; float: left; }
            .navbar nav { float: right; margin-top: 8px; }
            .navbar nav a { color: #2c2621; text-decoration: none; margin-left: 20px; font-size: 11pt; font-weight: 500; transition: color 0.3s; }
            .navbar nav a:hover { color: #b89758; }
            
            /* Layout Container */
            .content-container { max-width: 1100px; margin: 40px auto; padding: 0 20px; clear: both; }
            
            /* Hero Section */
            .hero-section { text-align: center; margin-bottom: 50px; padding: 30px 0; }
            .hero-section h2 { font-family: 'Georgia', serif; font-size: 24pt; margin-bottom: 10px; }
            .hero-section p { color: #8c764d; font-style: italic; }
            
            /* Grid de Produtos */
            .products-grid { margin-right: -20px; }
            .products-grid::after { content: ""; display: table; clear: both; }
            .product-card { background: #ffffff; border: 1px solid #e1d9ce; width: 31%; float: left; margin-right: 2%; margin-bottom: 30px; border-radius: 4px; overflow: hidden; transition: transform 0.3s, box-shadow 0.3s; }
            .product-card:hover { box-shadow: 0 10px 20px rgba(44,38,33,0.05); }
            .product-img-placeholder { background-color: #2c2621; height: 200px; text-align: center; line-height: 200px; }
            .product-img-placeholder span { color: #b89758; font-family: 'Georgia', serif; font-size: 14pt; letter-spacing: 2px; }
            .product-info { padding: 20px; }
            .product-info h3 { font-size: 13pt; margin-bottom: 5px; }
            .volumetria { font-size: 9pt; color: #8c764d; font-weight: bold; margin-bottom: 10px; }
            .description { font-size: 10pt; color: #666; margin-bottom: 15px; height: 45px; overflow: hidden; }
            .price { font-size: 14pt; font-weight: bold; color: #2c2621; margin-bottom: 15px; }
            
            /* Botoes e Alertas */
            .btn-primary { background-color: #b89758; color: #ffffff; border: none; width: 100%; padding: 12px; font-size: 10.5pt; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; cursor: pointer; border-radius: 2px; transition: background-color 0.3s; }
            .btn-primary:hover { background-color: #a48346; }
            .alert { padding: 15px; margin-bottom: 20px; border-radius: 4px; background-color: #f7f3eb; border: 1px solid #b89758; color: #8c764d; }
            
            /* Tabelas (Para Carrinho e Admin) */
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e1d9ce; }
            th { background-color: #f7f3eb; color: #8c764d; }
            
            /* Rodape */
            .main-footer { text-align: center; padding: 40px 0; border-top: 1px solid #e1d9ce; margin-top: 60px; font-size: 9pt; color: #8c764d; clear: both; }
        </style>
    </head>
    <body>
        <header class="navbar">
            <div class="nav-container">
                <a href="/" class="logo-text">OLIVA</a>
                <nav>
                    <a href="/">Catálogo</a>
                    <a href="/carrinho">Carrinho</a>
                    <a href="/login">Login</a>
                </nav>
            </div>
        </header>
        <main class="content-container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </main>
        <footer class="main-footer">
            <p>&copy; 2026 OLIVA - Fragrância em Decants. Todos os direitos reservados.</p>
        </footer>
    </body>
    </html>
    ''',
    
    'index.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <div class="hero-section">
        <h2>Fragrância em Decants</h2>
        <p>Experimente a sofisticação das maiores grifes do mundo na volumetria perfeita para você.</p>
    </div>
    <div class="products-grid">
        {% for produto in produtos %}
        <div class="product-card">
            <div class="product-img-placeholder"><span>OLIVA</span></div>
            <div class="product-info">
                <h3>{{ produto.nome }}</h3>
                <p class="volumetria">{{ produto.volume_ml }}ml</p>
                <p class="description">{{ produto.descricao }}</p>
                <p class="price">R$ {{ "%.2f"|format(produto.preco) }}</p>
                <form action="{{ url_for('adicionar_carrinho', id_produto=produto.id) }}" method="POST">
                    <button type="submit" class="btn-primary">Adicionar ao Carrinho</button>
                </form>
            </div>
        </div>
        {% else %}
        <p style="text-align: center; width: 100%; color: #8c764d;">Nenhum decant disponível no catálogo.</p>
        {% endfor %}
    </div>
    {% endblock %}
    ''',
    
    'carrinho.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2>Seu Carrinho</h2>
    <br>
    {% if produtos %}
        <table>
            <tr><th>Produto</th><th>Volumetria</th><th>Qtd</th><th>Subtotal</th></tr>
            {% for p in produtos %}
            <tr>
                <td>{{ p.nome }}</td>
                <td>{{ p.volume_ml }}ml</td>
                <td>{{ p.quantidade }}</td>
                <td>R$ {{ "%.2f"|format(p.subtotal) }}</td>
            </tr>
            {% endfor %}
        </table>
        <h3 style="text-align: right; margin-bottom: 20px;">Total: R$ {{ "%.2f"|format(total) }}</h3>
        <div style="text-align: right;">
            <a href="/carrinho/limpar" style="color: #d9534f; margin-right: 20px; text-decoration: none;">Esvaziar Carrinho</a>
            <button class="btn-primary" style="width: 200px;" onclick="alert('Módulo de pagamento em construção!')">Finalizar Compra</button>
        </div>
    {% else %}
        <p>Seu carrinho está vazio. Volte ao <a href="/" style="color: #b89758;">catálogo</a>.</p>
    {% endif %}
    {% endblock %}
    ''',

    'login.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <div style="max-width: 400px; margin: 0 auto; background: #fff; padding: 30px; border: 1px solid #e1d9ce; border-radius: 4px;">
        <h2 style="text-align: center; margin-bottom: 20px;">Acesso ao Sistema</h2>
        <form method="POST" action="/login">
            <p style="margin-bottom: 5px; font-weight: bold;">E-mail</p>
            <input type="email" name="email" required style="width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc;">
            <p style="margin-bottom: 5px; font-weight: bold;">Senha</p>
            <input type="password" name="senha" required style="width: 100%; padding: 10px; margin-bottom: 20px; border: 1px solid #ccc;">
            <button type="submit" class="btn-primary">Entrar</button>
        </form>
    </div>
    {% endblock %}
    ''',

    'admin.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2>Dashboard Gerencial</h2>
    <p>Área restrita de controle de estoque.</p>
    <br><br>
    <a href="/logout" style="color: #d9534f; text-decoration: none;">Sair do Sistema</a>
    {% endblock %}
    ''',

    'pedidos.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2>Meus Pedidos</h2>
    <p>Histórico de compras do cliente.</p>
    <br><br>
    <a href="/logout" style="color: #d9534f; text-decoration: none;">Sair</a>
    {% endblock %}
    '''
}

# Configura o Flask para usar o dicionário acima em vez de procurar pastas
app.jinja_loader = jinja2.DictLoader(TEMPLATES)


# ==========================================
# 2. CONFIGURAÇÃO E INICIALIZAÇÃO DO BANCO
# ==========================================

def get_db_connection():
    # Pega o link do banco que colocamos nas variáveis do Railway
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        );
    ''')
    
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
    
    cur.execute('SELECT COUNT(*) FROM produtos;')
    if cur.fetchone()[0] == 0:
        cur.execute('''
            INSERT INTO produtos (nome, descricao, preco, volume_ml, estoque, imagem_url) 
            VALUES ('Oliva Imperial', 'Notas amadeiradas com especiarias raras.', 189.90, 10, 50, 'perfume.jpg');
        ''')
    
    conn.commit()
    cur.close()
    conn.close()

try:
    init_db()
    print("Banco de dados verificado/inicializado com sucesso!")
except Exception as e:
    print(f"Aguardando conexão com o banco... {e}")


# ==========================================
# 3. ROTAS E LÓGICA DO SISTEMA
# ==========================================

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

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
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

@app.route('/meus-pedidos')
@login_required
def meus_pedidos():
    return render_template('pedidos.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
