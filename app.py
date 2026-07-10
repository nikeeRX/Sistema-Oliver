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
            .nav-container { max-width: 1100px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
            .logo-text { font-family: 'Georgia', serif; font-size: 20pt; font-weight: bold; color: #2c2621; text-decoration: none; letter-spacing: 3px; }
            .navbar nav a { color: #2c2621; text-decoration: none; margin-left: 20px; font-size: 11pt; font-weight: 500; transition: color 0.3s; }
            .navbar nav a:hover { color: #b89758; }
            
            /* Layout Container */
            .content-container { max-width: 1100px; margin: 40px auto; padding: 0 20px; min-height: 60vh; }
            
            /* Hero Section e Títulos */
            .hero-section { text-align: center; margin-bottom: 50px; padding: 30px 0; }
            .hero-section h2 { font-family: 'Georgia', serif; font-size: 24pt; margin-bottom: 10px; }
            .hero-section p { color: #8c764d; font-style: italic; }
            .page-title { font-family: 'Georgia', serif; font-size: 20pt; border-left: 4px solid #b89758; padding-left: 15px; margin-bottom: 25px; }
            
            /* Grid de Produtos */
            .products-grid { display: flex; flex-wrap: wrap; gap: 2%; }
            .product-card { background: #ffffff; border: 1px solid #e1d9ce; width: 31%; margin-bottom: 30px; border-radius: 4px; overflow: hidden; transition: transform 0.3s, box-shadow 0.3s; }
            .product-card:hover { box-shadow: 0 10px 20px rgba(44,38,33,0.05); }
            .product-img-placeholder { background-color: #2c2621; height: 200px; display: flex; align-items: center; justify-content: center; }
            .product-img-placeholder span { color: #b89758; font-family: 'Georgia', serif; font-size: 14pt; letter-spacing: 2px; }
            .product-info { padding: 20px; }
            .product-info h3 { font-size: 13pt; margin-bottom: 5px; }
            .volumetria { font-size: 9pt; color: #8c764d; font-weight: bold; margin-bottom: 10px; }
            .description { font-size: 10pt; color: #666; margin-bottom: 15px; height: 45px; overflow: hidden; }
            .price { font-size: 14pt; font-weight: bold; color: #2c2621; margin-bottom: 15px; }
            
            /* Dashboard Cards */
            .dashboard-cards { display: flex; gap: 20px; margin-bottom: 40px; }
            .card { background: #ffffff; padding: 25px; border: 1px solid #e1d9ce; border-left: 4px solid #b89758; flex: 1; border-radius: 4px; }
            .card h3 { color: #8c764d; font-size: 11pt; margin-bottom: 10px; text-transform: uppercase; }
            .card p { font-size: 24pt; font-weight: bold; color: #2c2621; }
            
            /* Formulários */
            .form-group { margin-bottom: 15px; }
            label { display: block; font-weight: bold; margin-bottom: 5px; font-size: 10pt; color: #666; }
            input, textarea { width: 100%; padding: 10px; border: 1px solid #dfd5c6; border-radius: 4px; font-family: inherit; }
            
            /* Botoes e Alertas */
            .btn-primary { background-color: #b89758; color: #ffffff; border: none; width: 100%; padding: 12px; font-size: 10.5pt; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; cursor: pointer; border-radius: 2px; transition: background-color 0.3s; }
            .btn-primary:hover { background-color: #a48346; }
            .alert { padding: 15px; margin-bottom: 20px; border-radius: 4px; background-color: #f7f3eb; border: 1px solid #b89758; color: #8c764d; }
            
            /* Tabelas */
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; background: #fff; border: 1px solid #e1d9ce; }
            th, td { padding: 15px; text-align: left; border-bottom: 1px solid #e1d9ce; }
            th { background-color: #f7f3eb; color: #8c764d; font-size: 10pt; text-transform: uppercase; }
            tr:hover { background-color: #fcfbf9; }
            
            /* Rodape */
            .main-footer { text-align: center; padding: 40px 0; border-top: 1px solid #e1d9ce; margin-top: 60px; font-size: 9pt; color: #8c764d; }
        </style>
    </head>
    <body>
        <header class="navbar">
            <div class="nav-container">
                <a href="/" class="logo-text">OLIVA</a>
                <nav>
                    <a href="/">Catálogo</a>
                    {% if session.get('usuario_id') %}
                        {% if session.get('is_admin') %}
                            <a href="/admin/dashboard">Dashboard</a>
                            <a href="/admin/estoque">Estoque</a>
                            <a href="/admin/comissao">Comissões</a>
                        {% else %}
                            <a href="/carrinho">Carrinho</a>
                            <a href="/meus-pedidos">Meus Pedidos</a>
                        {% endif %}
                        <a href="/logout" style="color: #d9534f;">Sair</a>
                    {% else %}
                        <a href="/carrinho">Carrinho</a>
                        <a href="/login">Login</a>
                    {% endif %}
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
                <p class="volumetria">{{ produto.volume_ml }}ml | Em Estoque: {{ produto.estoque }}</p>
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
    <h2 class="page-title">Seu Carrinho</h2>
    {% if produtos %}
        <table>
            <tr><th>Produto</th><th>Volumetria</th><th>Qtd</th><th>Subtotal</th></tr>
            {% for p in produtos %}
            <tr>
                <td><strong>{{ p.nome }}</strong></td>
                <td>{{ p.volume_ml }}ml</td>
                <td>{{ p.quantidade }}</td>
                <td>R$ {{ "%.2f"|format(p.subtotal) }}</td>
            </tr>
            {% endfor %}
        </table>
        <h3 style="text-align: right; margin-bottom: 20px; color: #2c2621;">Total a Pagar: R$ {{ "%.2f"|format(total) }}</h3>
        <div style="text-align: right;">
            <a href="/carrinho/limpar" style="color: #d9534f; margin-right: 20px; text-decoration: none; font-weight: bold;">Esvaziar Carrinho</a>
            <button class="btn-primary" style="width: 250px;" onclick="alert('Módulo de pagamento em construção para a próxima fase!')">Finalizar Compra</button>
        </div>
    {% else %}
        <div style="text-align: center; padding: 50px;">
            <p style="font-size: 14pt; color: #666; margin-bottom: 20px;">Seu carrinho está vazio.</p>
            <a href="/" style="color: #b89758; font-weight: bold; text-decoration: none;">Voltar ao catálogo</a>
        </div>
    {% endif %}
    {% endblock %}
    ''',

    'login.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <div style="max-width: 400px; margin: 0 auto; background: #fff; padding: 40px; border: 1px solid #e1d9ce; border-radius: 4px; margin-top: 50px;">
        <h2 style="text-align: center; margin-bottom: 30px; font-family: 'Georgia', serif; color: #2c2621;">Acesso ao Sistema</h2>
        <form method="POST" action="/login">
            <div class="form-group">
                <label>E-mail de Acesso</label>
                <input type="email" name="email" required placeholder="ex: admin@oliva.com">
            </div>
            <div class="form-group" style="margin-bottom: 30px;">
                <label>Senha</label>
                <input type="password" name="senha" required placeholder="Sua senha">
            </div>
            <button type="submit" class="btn-primary">Entrar na Plataforma</button>
        </form>
        <p style="text-align: center; margin-top: 20px; font-size: 9pt; color: #8c764d;">Dica: Use admin@oliva.com / admin123</p>
    </div>
    {% endblock %}
    ''',

    'admin.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Dashboard Gerencial</h2>
    
    <div class="dashboard-cards">
        <div class="card">
            <h3>Total de Decants no Catálogo</h3>
            <p>{{ total_produtos }}</p>
        </div>
        <div class="card">
            <h3>Volume Total em Estoque (Unid)</h3>
            <p>{{ estoque_total }}</p>
        </div>
        <div class="card">
            <h3>Vendas Realizadas</h3>
            <p>0</p> </div>
    </div>
    
    <p style="color: #666; font-size: 11pt;">Bem-vindo ao centro de comando da OLIVA. Utilize o menu superior para gerenciar seu estoque e analisar as comissões geradas pela operação.</p>
    {% endblock %}
    ''',
    
    'estoque.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Controle de Estoque</h2>
    
    <div style="background: #fff; padding: 25px; border: 1px solid #e1d9ce; margin-bottom: 40px; border-radius: 4px;">
        <h3 style="margin-bottom: 15px; color: #8c764d;">Cadastrar Novo Decant</h3>
        <form method="POST" action="/admin/estoque" style="display: flex; flex-wrap: wrap; gap: 15px;">
            <div class="form-group" style="flex: 1; min-width: 200px;">
                <label>Nome da Fragrância</label>
                <input type="text" name="nome" required>
            </div>
            <div class="form-group" style="width: 100px;">
                <label>Volume (ml)</label>
                <input type="number" name="volume_ml" required>
            </div>
            <div class="form-group" style="width: 150px;">
                <label>Preço (R$)</label>
                <input type="number" step="0.01" name="preco" required>
            </div>
            <div class="form-group" style="width: 100px;">
                <label>Estoque</label>
                <input type="number" name="estoque" required>
            </div>
            <div class="form-group" style="width: 100%;">
                <label>Descrição Olfativa</label>
                <textarea name="descricao" rows="2"></textarea>
            </div>
            <button type="submit" class="btn-primary" style="width: 200px;">Salvar Produto</button>
        </form>
    </div>

    <h3>Inventário Atual</h3>
    <br>
    <table>
        <tr><th>ID</th><th>Produto</th><th>Vol</th><th>Preço</th><th>Estoque</th><th>Ação</th></tr>
        {% for p in produtos %}
        <tr>
            <td>#{{ p.id }}</td>
            <td><strong>{{ p.nome }}</strong></td>
            <td>{{ p.volume_ml }}ml</td>
            <td>R$ {{ "%.2f"|format(p.preco) }}</td>
            <td><span style="padding: 5px 10px; background: {% if p.estoque < 5 %}#fff0f0{% else %}#eefaf2{% endif %}; border-radius: 20px; font-weight: bold;">{{ p.estoque }} un</span></td>
            <td><a href="#" style="color: #b89758; text-decoration: none;">Editar</a></td>
        </tr>
        {% endfor %}
    </table>
    {% endblock %}
    ''',
    
    'comissao.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Relatório de Comissão de Vendas</h2>
    
    <div class="alert" style="background: #eefaf2; border-color: #4cae4c; color: #3c763d;">
        <strong>Simulação Ativa:</strong> As comissões abaixo estão projetadas com base em <strong>10%</strong> do valor de tabela dos produtos cadastrados no estoque atual.
    </div>

    <table>
        <tr><th>ID Prod</th><th>Fragrância Vendida</th><th>Valor da Venda</th><th>Taxa</th><th>Sua Comissão Estimada</th></tr>
        {% for p in produtos %}
        <tr>
            <td>#{{ p.id }}</td>
            <td>{{ p.nome }} ({{ p.volume_ml }}ml)</td>
            <td>R$ {{ "%.2f"|format(p.preco) }}</td>
            <td>10%</td>
            <td style="color: #2b542c; font-weight: bold; font-size: 12pt;">R$ {{ "%.2f"|format(p.preco * 0.10) }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endblock %}
    ''',

    'pedidos.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Meus Pedidos</h2>
    <div style="background: #fff; padding: 40px; text-align: center; border: 1px dashed #ccc;">
        <p style="color: #666;">Você ainda não possui pedidos finalizados.</p>
        <br>
        <a href="/" class="btn-primary" style="text-decoration: none; padding: 10px 30px;">Explorar Catálogo</a>
    </div>
    {% endblock %}
    '''
}

app.jinja_loader = jinja2.DictLoader(TEMPLATES)


# ==========================================
# 2. CONFIGURAÇÃO E INICIALIZAÇÃO DO BANCO
# ==========================================

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Cria tabelas se não existirem
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
    
    # Cria a conta de Administrador automaticamente para você testar (se não existir)
    cur.execute('SELECT COUNT(*) FROM usuarios;')
    if cur.fetchone()[0] == 0:
        senha_hash = generate_password_hash('admin123')
        cur.execute('''
            INSERT INTO usuarios (nome, email, senha, is_admin)
            VALUES ('Admin Oliva', 'admin@oliva.com', %s, TRUE);
        ''', (senha_hash,))

    # Insere produto teste apenas se a tabela estiver vazia
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
    print("Banco e tabelas iniciais prontos para operação!")
except Exception as e:
    print(f"Aguardando conexão com banco... {e}")


# ==========================================
# 3. ROTAS DE SEGURANÇA E PROTEÇÃO
# ==========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, faça o login para acessar esta área.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or not session.get('is_admin'):
            flash('Acesso bloqueado. Área restrita à diretoria.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# 4. ROTAS PÚBLICAS (VITRINE E CARRINHO)
# ==========================================

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
    
    flash("Fragrância separada no seu carrinho!", "success")
    return redirect(url_for('index'))

@app.route('/carrinho/limpar')
def limpar_carrinho():
    session.pop('carrinho', None)
    return redirect(url_for('carrinho'))


# ==========================================
# 5. ROTAS DE AUTENTICAÇÃO
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
            
            flash(f"Bem-vindo de volta, {usuario['nome']}!", "success")
            if usuario['is_admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('meus_pedidos'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com segurança.', 'success')
    return redirect(url_for('index'))


# ==========================================
# 6. ROTAS DO CLIENTE
# ==========================================

@app.route('/meus-pedidos')
@login_required
def meus_pedidos():
    return render_template('pedidos.html')


# ==========================================
# 7. ROTAS DO PAINEL GERENCIAL (ADMIN)
# ==========================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM produtos;')
    total_produtos = cur.fetchone()[0]
    
    cur.execute('SELECT SUM(estoque) FROM produtos;')
    estoque_total = cur.fetchone()[0] or 0
    
    cur.close()
    conn.close()
    return render_template('admin.html', total_produtos=total_produtos, estoque_total=estoque_total)

@app.route('/admin/estoque', methods=['GET', 'POST'])
@admin_required
def admin_estoque():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Processa o formulário de cadastro de novo produto
    if request.method == 'POST':
        nome = request.form['nome']
        volume_ml = request.form['volume_ml']
        preco = request.form['preco']
        estoque = request.form['estoque']
        descricao = request.form.get('descricao', '')
        
        cur.execute('''
            INSERT INTO produtos (nome, descricao, preco, volume_ml, estoque)
            VALUES (%s, %s, %s, %s, %s);
        ''', (nome, descricao, preco, volume_ml, estoque))
        conn.commit()
        flash(f'{nome} adicionado ao estoque com sucesso!', 'success')
        return redirect(url_for('admin_estoque'))
    
    # Carrega a tabela de inventário
    cur.execute('SELECT * FROM produtos ORDER BY id DESC;')
    produtos = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('estoque.html', produtos=produtos)

@app.route('/admin/comissao')
@admin_required
def admin_comissao():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    # Busca os produtos para simular uma tabela de comissões
    cur.execute('SELECT id, nome, preco, volume_ml FROM produtos ORDER BY preco DESC;')
    produtos = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('comissao.html', produtos=produtos)


# ==========================================
# INICIAR O MOTOR
# ==========================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
