import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jinja2
from datetime import datetime
import base64

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
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <title>OLIVA - Fragrância em Decants</title>
        <style>
            body, h1, h2, h3, p, ul, form { margin: 0; padding: 0; box-sizing: border-box; }
            /* Adicionado Flexbox no Body para garantir o Rodapé sempre no fundo */
            body { background-color: #fcfaf7; color: #332d27; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 300; -webkit-font-smoothing: antialiased; display: flex; flex-direction: column; min-height: 100vh; }
            
            .navbar { background-color: transparent; padding: 25px 0; border-bottom: 1px solid #eae1d3; }
            .nav-container { max-width: 1100px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; width: 100%; }
            .logo-text { font-family: 'Times New Roman', Georgia, serif; font-size: 26pt; color: #b89758; text-decoration: none; letter-spacing: 8px; text-transform: uppercase; }
            .navbar nav a { color: #665b4f; text-decoration: none; margin-left: 20px; font-size: 10pt; letter-spacing: 1px; text-transform: uppercase; transition: color 0.3s; }
            .navbar nav a:hover { color: #b89758; }
            
            /* O flex: 1 empurra o rodapé para baixo independentemente do conteúdo */
            .content-container { max-width: 1100px; width: 100%; margin: 40px auto; padding: 0 20px; flex: 1; }
            
            .hero-section { text-align: center; margin-bottom: 50px; padding: 10px 0; }
            .hero-section h2 { font-family: 'Times New Roman', Georgia, serif; font-size: 22pt; margin-bottom: 15px; color: #2c2621; letter-spacing: 2px; }
            .hero-section p { color: #8c764d; font-style: italic; font-size: 11pt; letter-spacing: 1px; }
            .page-title { font-family: 'Times New Roman', Georgia, serif; font-size: 20pt; margin-bottom: 30px; color: #2c2621; letter-spacing: 1px; text-align: center; }
            
            .products-grid { display: flex; flex-wrap: wrap; gap: 2%; }
            .product-card { background: #ffffff; border: 1px solid #f2ecdf; width: 32%; margin-bottom: 30px; border-radius: 6px; overflow: hidden; transition: all 0.3s ease; }
            .product-card:hover { transform: translateY(-5px); box-shadow: 0 12px 25px rgba(184, 151, 88, 0.1); border-color: #dfd5c6; }
            .product-img-placeholder { background: linear-gradient(135deg, #fffcf7 0%, #f4ede1 100%); height: 260px; display: flex; flex-direction: column; align-items: center; justify-content: center; border-bottom: 1px solid #f2ecdf; }
            .img-icon { font-size: 28pt; color: #b89758; margin-bottom: 10px; }
            .product-img-placeholder span.marca { color: #8c764d; font-family: 'Times New Roman', serif; font-size: 11pt; letter-spacing: 4px; text-transform: uppercase; }
            .product-img-real { height: 260px; width: 100%; border-bottom: 1px solid #f2ecdf; display: flex; align-items: center; justify-content: center; overflow: hidden; }
            .product-img-real img { width: 100%; height: 100%; object-fit: cover; }
            
            .product-info { padding: 25px 20px; text-align: center; }
            .product-info h3 { font-size: 13pt; margin-bottom: 8px; color: #2c2621; font-weight: 500; }
            .volumetria { font-size: 8.5pt; color: #b89758; font-weight: bold; margin-bottom: 12px; }
            .description { font-size: 9.5pt; color: #7a7065; margin-bottom: 20px; height: 42px; overflow: hidden; }
            .price { font-size: 14pt; color: #2c2621; margin-bottom: 20px; font-family: 'Times New Roman', serif; }
            
            .dashboard-cards { display: flex; gap: 20px; margin-bottom: 40px; }
            .card { background: #ffffff; padding: 30px; border: 1px solid #eae1d3; border-top: 3px solid #b89758; flex: 1; border-radius: 6px; text-align: center; }
            .card h3 { color: #8c764d; font-size: 9pt; margin-bottom: 15px; letter-spacing: 2px; }
            .card p { font-size: 26pt; color: #2c2621; font-family: 'Times New Roman', serif; }
            
            .form-row { display: flex; flex-wrap: wrap; gap: 15px; }
            .col-100 { width: 100%; }
            .col-50 { width: calc(50% - 7.5px); }
            .form-group { margin-bottom: 15px; text-align: left; }
            label { display: block; font-weight: 500; margin-bottom: 8px; font-size: 9pt; color: #665b4f; text-transform: uppercase; letter-spacing: 1px; }
            input, textarea, select { width: 100%; padding: 12px; border: 1px solid #dfd5c6; border-radius: 4px; font-family: inherit; background-color: #fffcf7; font-size: 11pt; }
            input:focus, textarea:focus, select:focus { outline: none; border-color: #b89758; }
            
            .btn-primary { background-color: #b89758; color: #ffffff; border: none; width: 100%; padding: 15px; font-size: 9pt; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; cursor: pointer; border-radius: 4px; transition: all 0.3s; }
            .btn-primary:hover { background-color: #2c2621; color: #b89758; }
            .btn-secondary { background-color: transparent; color: #665b4f; border: 1px solid #dfd5c6; padding: 14px 20px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; text-transform: uppercase; font-size: 9pt; text-align: center; }
            .btn-secondary:hover { background-color: #f2ecdf; }
            
            .alert { padding: 15px; margin-bottom: 25px; border-radius: 4px; background-color: #fdfbf7; border-left: 4px solid #b89758; color: #665b4f; font-size: 10pt; width: 100%; }
            .alert-error { border-left-color: #d9534f; color: #d9534f; background-color: #fff0f0; }
            
            .table-wrapper { width: 100%; overflow-x: auto; margin-bottom: 30px; border-radius: 6px; background: #fff; border: 1px solid #f2ecdf; }
            table { width: 100%; border-collapse: collapse; min-width: 600px; }
            th, td { padding: 16px 15px; text-align: left; border-bottom: 1px solid #f2ecdf; white-space: nowrap; }
            th { background-color: #fffcf7; color: #8c764d; font-size: 9pt; text-transform: uppercase; font-weight: 500; }
            
            /* Rodapé com formatação blindada */
            .main-footer { text-align: center; padding: 40px 0; margin-top: auto; font-size: 9pt; color: #a39686; border-top: 1px solid #eae1d3; letter-spacing: 1px; width: 100%; background-color: #fcfaf7; }
            
            @media (max-width: 768px) {
                .nav-container { flex-direction: column; gap: 15px; text-align: center; }
                .navbar nav { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; }
                .navbar nav a { margin: 0; font-size: 9pt; }
                .product-card { width: 48%; }
                .col-50 { width: 100%; }
                .dashboard-cards { flex-direction: column; gap: 15px; }
            }
            @media (max-width: 480px) { .product-card { width: 100%; } }
        </style>
    </head>
    <body>
        <header class="navbar">
            <div class="nav-container">
                <a href="/" class="logo-text">OLIVA</a>
                <nav>
                    <a href="/">Catálogo</a>
                    {% if session.get('usuario_id') %}
                        {% if session.get('tipo') == 'admin' %}
                            <a href="/admin/dashboard">Painel</a>
                            <a href="/admin/estoque">Estoque</a>
                            <a href="/admin/aprovacoes">Aprovações</a>
                        {% elif session.get('tipo') == 'vendedor' %}
                            <a href="/carrinho">Carrinho</a>
                            <a href="/admin/comissao">Minhas Comissões</a>
                        {% else %}
                            <a href="/carrinho">Carrinho</a>
                            <a href="/meus-pedidos">Pedidos</a>
                        {% endif %}
                        <a href="/logout" style="color: #d9534f;">Sair</a>
                    {% else %}
                        <a href="/carrinho">Carrinho</a>
                        <a href="/login">Entrar / Criar Conta</a>
                        <a href="/seja-revendedor" style="color: #b89758; font-weight: bold;">Seja Revendedor(a)</a>
                    {% endif %}
                </nav>
            </div>
        </header>
        <main class="content-container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert {% if category == 'error' %}alert-error{% endif %}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </main>
        <footer class="main-footer">
            <p>OLIVA &copy; 2026. A ARTE DA FRAGRÂNCIA.</p>
        </footer>
    </body>
    </html>
    ''',
    
    'index.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <div class="hero-section">
        <h2>A Essência da Exclusividade</h2>
        <p>A sofisticação das maiores grifes do mundo, na volumetria perfeita.</p>
    </div>
    <div class="products-grid">
        {% for produto in produtos %}
        <div class="product-card">
            {% if produto.imagem_base64 %}
                <div class="product-img-real"><img src="data:image/jpeg;base64,{{ produto.imagem_base64 }}" alt="{{ produto.nome }}"></div>
            {% else %}
                <div class="product-img-placeholder"><div class="img-icon">✧</div><span class="marca">OLIVA</span></div>
            {% endif %}
            <div class="product-info">
                <h3>{{ produto.nome }}</h3>
                <p class="volumetria">{{ produto.volume_ml }}ML &nbsp;|&nbsp; ESTOQUE: {{ produto.estoque }}</p>
                <p class="description">{{ produto.descricao }}</p>
                <p class="price">R$ {{ "%.2f"|format(produto.preco) }}</p>
                <form action="{{ url_for('adicionar_carrinho', id_produto=produto.id) }}" method="POST">
                    <button type="submit" class="btn-primary">Adicionar</button>
                </form>
            </div>
        </div>
        {% else %}
        <p style="text-align: center; width: 100%; color: #8c764d; font-style: italic;">Nosso catálogo está sendo atualizado.</p>
        {% endfor %}
    </div>
    {% endblock %}
    ''',
    
    'carrinho.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Meu Carrinho</h2>
    {% if produtos %}
        <div class="table-wrapper">
            <table>
                <tr><th>Fragrância</th><th>Vol (ml)</th><th>Qtd</th><th>Subtotal</th></tr>
                {% for p in produtos %}
                <tr>
                    <td style="color: #2c2621; font-weight: 500;">{{ p.nome }}</td>
                    <td style="color: #8c764d;">{{ p.volume_ml }}</td>
                    <td>{{ p.quantidade }}</td>
                    <td style="font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(p.subtotal) }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <h3 style="text-align: right; margin-bottom: 20px; color: #2c2621; font-family: 'Times New Roman', serif; font-size: 16pt;">Total: R$ {{ "%.2f"|format(total) }}</h3>
        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 15px;">
            <a href="/checkout" class="btn-primary" style="max-width: 300px; text-align: center; text-decoration: none; box-sizing: border-box;">Avançar para Pagamento</a>
            <a href="/carrinho/limpar" style="color: #a39686; text-decoration: none; font-size: 9pt; text-transform: uppercase;">Esvaziar Carrinho</a>
        </div>
    {% else %}
        <div style="text-align: center; padding: 60px 0;">
            <p style="font-size: 12pt; color: #a39686; margin-bottom: 30px; font-style: italic;">Seu carrinho está vazio.</p>
            <a href="/" class="btn-primary" style="text-decoration: none; display: inline-block; width: auto; padding: 15px 40px;">Ver Catálogo</a>
        </div>
    {% endif %}
    {% endblock %}
    ''',

    'login.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <div style="display: flex; flex-wrap: wrap; gap: 30px; max-width: 900px; margin: 0 auto; margin-top: 40px;">
        
        <div style="flex: 1; min-width: 300px; background: #fff; padding: 40px; border: 1px solid #f2ecdf; border-radius: 6px;">
            <h2 style="text-align: center; margin-bottom: 30px; font-family: 'Times New Roman', serif; color: #2c2621;">Já tenho cadastro</h2>
            <form method="POST" action="/login">
                <div class="form-group"><label>E-mail</label><input type="email" name="email" required></div>
                <div class="form-group" style="margin-bottom: 30px;"><label>Senha</label><input type="password" name="senha" required></div>
                <button type="submit" class="btn-primary">Entrar</button>
            </form>
        </div>

        <div style="flex: 1; min-width: 300px; background: #fff; padding: 40px; border: 1px solid #f2ecdf; border-radius: 6px;">
            <h2 style="text-align: center; margin-bottom: 30px; font-family: 'Times New Roman', serif; color: #2c2621;">Criar Conta de Cliente</h2>
            <form method="POST" action="/cadastro/cliente">
                <div class="form-group"><label>Nome Completo</label><input type="text" name="nome" required></div>
                <div class="form-group"><label>E-mail</label><input type="email" name="email" required></div>
                <div class="form-group"><label>WhatsApp</label><input type="text" name="whatsapp" required placeholder="(00) 00000-0000"></div>
                <div class="form-group" style="margin-bottom: 30px;"><label>Crie uma Senha</label><input type="password" name="senha" required></div>
                <button type="submit" class="btn-secondary" style="width: 100%;">Finalizar Cadastro</button>
            </form>
        </div>
    </div>
    {% endblock %}
    ''',

    'revendedor.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <div style="max-width: 600px; margin: 20px auto; background: #fff; padding: 40px; border: 1px solid #f2ecdf; border-radius: 6px; box-shadow: 0 10px 30px rgba(0,0,0,0.02);">
        <h2 style="text-align: center; margin-bottom: 20px; font-family: 'Times New Roman', serif; color: #b89758;">Seja um(a) Revendedor(a) OLIVA</h2>
        <p style="text-align: center; color: #666; margin-bottom: 30px; font-size: 11pt;">Preencha o formulário abaixo. Sua solicitação passará por uma análise exclusiva da nossa diretoria.</p>
        
        <form method="POST" action="/cadastro/revendedor" class="form-row">
            <div class="form-group col-100"><label>Nome Completo</label><input type="text" name="nome" required></div>
            <div class="form-group col-50"><label>CPF</label><input type="text" name="cpf" required placeholder="000.000.000-00"></div>
            <div class="form-group col-50"><label>WhatsApp</label><input type="text" name="whatsapp" required placeholder="(00) 00000-0000"></div>
            <div class="form-group col-100"><label>E-mail de Trabalho</label><input type="email" name="email" required></div>
            <div class="form-group col-100" style="margin-bottom: 30px;"><label>Crie uma Senha de Acesso</label><input type="password" name="senha" required></div>
            <div class="col-100"><button type="submit" class="btn-primary" style="background-color: #2c2621; color: #b89758;">Enviar Solicitação</button></div>
        </form>
    </div>
    {% endblock %}
    ''',

    'admin.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Visão Gerencial</h2>
    <div class="dashboard-cards">
        <div class="card">
            <h3>Fragrâncias Ativas</h3>
            <p>{{ total_produtos }}</p>
        </div>
        <div class="card">
            <h3>Volume em Estoque (Unid)</h3>
            <p>{{ estoque_total }}</p>
        </div>
        <div class="card">
            <h3>Revendedores Pendentes</h3>
            <p style="color: #d9534f;">{{ pendentes }}</p>
        </div>
    </div>
    {% endblock %}
    ''',

    'admin_aprovacoes.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Aprovação de Revendedores</h2>
    <div class="alert" style="background: #fff; border-left-color: #2c2621;">
        Gerencie as contas que solicitaram acesso ao programa de comissões e vendas exclusivas.
    </div>
    <div class="table-wrapper">
        <table>
            <tr><th>Data</th><th>Nome</th><th>CPF / WhatsApp</th><th>Email</th><th>Ação</th></tr>
            {% for v in revendedores %}
            <tr>
                <td style="color: #a39686;">{{ v.id }}</td>
                <td style="color: #2c2621; font-weight: 500;">{{ v.nome }}</td>
                <td style="color: #666;">{{ v.cpf }}<br><span style="font-size: 9pt;">{{ v.whatsapp }}</span></td>
                <td>{{ v.email }}</td>
                <td>
                    <form action="/admin/aprovar/{{ v.id }}" method="POST" style="display:inline;">
                        <button type="submit" class="btn-primary" style="padding: 8px 15px; width: auto; font-size: 8pt;">Aprovar</button>
                    </form>
                </td>
            </tr>
            {% else %}
            <tr><td colspan="5" style="text-align: center; color: #a39686; font-style: italic;">Nenhuma solicitação pendente.</td></tr>
            {% endfor %}
        </table>
    </div>
    {% endblock %}
    ''',

    'estoque.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Gestão de Estoque</h2>
    
    <div style="display: flex; flex-direction: column; gap: 30px; margin-bottom: 50px;">
        
        <div style="background: #fff; padding: 30px 20px; border: 1px solid #f2ecdf; border-radius: 6px;">
            <h3 style="margin-bottom: 20px; color: #2c2621; font-family: 'Times New Roman', serif; font-size: 15pt;">1. Cadastrar Novo Decant</h3>
            <form method="POST" action="/admin/estoque" enctype="multipart/form-data" class="form-row">
                <input type="hidden" name="action" value="novo_produto">
                <div class="form-group col-100"><label>Nome do Perfume</label><input type="text" name="nome" required></div>
                <div class="form-group col-50"><label>Volumetria (ml)</label><input type="number" name="volume_ml" required></div>
                <div class="form-group col-50"><label>Estoque Inicial</label><input type="number" name="estoque" required value="0"></div>
                <div class="form-group col-50"><label>Custo Pago (R$)</label><input type="number" step="0.01" name="custo" required placeholder="0.00"></div>
                <div class="form-group col-50"><label>Preço Venda (R$)</label><input type="number" step="0.01" name="preco" required placeholder="0.00"></div>
                <div class="form-group col-100"><label>Foto do Produto</label><input type="file" name="imagem" accept="image/*"></div>
                <div class="form-group col-100"><label>Descrição Olfativa</label><textarea name="descricao" rows="2"></textarea></div>
                <div class="col-100"><button type="submit" class="btn-primary">Criar Cadastro</button></div>
            </form>
        </div>

        <div style="background: #fff; padding: 30px 20px; border: 1px solid #f2ecdf; border-radius: 6px;">
            <h3 style="margin-bottom: 20px; color: #2c2621; font-family: 'Times New Roman', serif; font-size: 15pt;">2. Registrar Reposição</h3>
            <form method="POST" action="/admin/estoque" class="form-row">
                <input type="hidden" name="action" value="nova_entrada">
                <div class="form-group col-100">
                    <label>Selecione a Fragrância</label>
                    <select name="produto_id" required>
                        <option value="">-- Escolha --</option>
                        {% for p in produtos %}
                            <option value="{{ p.id }}">{{ p.nome }} ({{ p.volume_ml }}ml)</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group col-100"><label>Data da Compra</label><input type="date" name="data_compra" required value="{{ data_hoje }}"></div>
                <div class="form-group col-50"><label>Qtd Comprada</label><input type="number" name="quantidade" required min="1"></div>
                <div class="form-group col-50"><label>Custo Unitário (R$)</label><input type="number" step="0.01" name="custo" required></div>
                <div class="col-100"><button type="submit" class="btn-primary" style="background-color: #2c2621; color: #b89758;">Gravar Estoque</button></div>
            </form>
        </div>
    </div>

    <h3 style="margin-bottom: 15px; color: #2c2621; font-family: 'Times New Roman', serif; font-size: 15pt;">Catálogo Atual & Edição</h3>
    <div class="table-wrapper">
        <table>
            <tr><th>Foto</th><th>Fragrância</th><th>Custo</th><th>Venda</th><th>Estoque</th><th>Ação</th></tr>
            {% for p in produtos %}
            <tr>
                <td>
                    {% if p.imagem_base64 %}
                        <img src="data:image/jpeg;base64,{{ p.imagem_base64 }}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #eae1d3;">
                    {% else %}
                        <div style="width: 40px; height: 40px; background: #fcfaf7; border: 1px solid #eae1d3; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 8pt; color: #b89758;">✧</div>
                    {% endif %}
                </td>
                <td style="color: #2c2621; font-weight: 500; white-space: normal; min-width: 150px;">{{ p.nome }} <span style="color: #8c764d; font-size: 9pt;">({{ p.volume_ml }}ml)</span></td>
                <td style="color: #666; font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(p.custo) if p.custo else "0.00" }}</td>
                <td style="font-family: 'Times New Roman', serif; color: #2c2621; font-weight: bold;">R$ {{ "%.2f"|format(p.preco) }}</td>
                <td>
                    <span style="padding: 4px 10px; background: {% if p.estoque < 5 %}#fffcf7{% else %}transparent{% endif %}; border: 1px solid {% if p.estoque < 5 %}#b89758{% else %}#eae1d3{% endif %}; border-radius: 4px; font-size: 9pt; color: #665b4f;">
                        {{ p.estoque }} un
                    </span>
                </td>
                <td>
                    <a href="/admin/produto/editar/{{ p.id }}" style="color: #b89758; text-decoration: none; font-size: 9pt; text-transform: uppercase; font-weight: bold;">Editar</a>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endblock %}
    ''',
    
    'editar_produto.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Editar Fragrância</h2>
    <div style="background: #fff; padding: 30px 20px; border: 1px solid #f2ecdf; border-radius: 6px; margin-bottom: 30px;">
        <form method="POST" action="/admin/produto/editar/{{ p.id }}" enctype="multipart/form-data" class="form-row">
            <div class="form-group col-100"><label>Nome do Perfume</label><input type="text" name="nome" required value="{{ p.nome }}"></div>
            <div class="form-group col-50"><label>Volumetria (ml)</label><input type="number" name="volume_ml" required value="{{ p.volume_ml }}"></div>
            <div class="form-group col-50"><label>Custo Base Atual (R$)</label><input type="number" step="0.01" name="custo" required value="{{ p.custo }}"></div>
            <div class="form-group col-100"><label>Preço Venda (R$)</label><input type="number" step="0.01" name="preco" required value="{{ p.preco }}"></div>
            <div class="form-group col-100">
                <label>Nova Foto (Deixe em branco para manter a atual)</label>
                <input type="file" name="imagem" accept="image/*">
            </div>
            <div class="form-group col-100"><label>Descrição Olfativa</label><textarea name="descricao" rows="4">{{ p.descricao }}</textarea></div>
            <div class="col-100" style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
                <button type="submit" class="btn-primary">Salvar Alterações</button>
                <a href="/admin/estoque" class="btn-secondary">Voltar sem Salvar</a>
            </div>
        </form>
    </div>
    {% endblock %}
    ''',
    
    'comissao.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Rentabilidade & Comissões</h2>
    <div class="alert" style="border-left-color: #2c2621; background-color: #fff;">
        <span style="color: #2c2621; font-weight: bold;">Análise de Lucro (10%)</span>
    </div>
    <div class="table-wrapper">
        <table>
            <tr><th>Fragrância</th><th>Custo Pago</th><th>Venda</th><th>Lucro</th><th>Comissão (10%)</th></tr>
            {% for p in produtos %}
            <tr>
                <td style="color: #2c2621; white-space: normal; min-width: 150px;">{{ p.nome }} <span style="color: #8c764d; font-size: 9pt;">({{ p.volume_ml }}ml)</span></td>
                <td style="color: #d9534f; font-family: 'Times New Roman', serif;">- R$ {{ "%.2f"|format(p.custo) if p.custo else "0.00" }}</td>
                <td style="color: #2c2621; font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(p.preco) }}</td>
                <td style="color: #3c763d; font-family: 'Times New Roman', serif; font-weight: bold;">R$ {{ "%.2f"|format(p.preco - (p.custo or 0)) }}</td>
                <td style="color: #b89758; font-family: 'Times New Roman', serif; font-weight: bold;">R$ {{ "%.2f"|format(p.preco * 0.10) }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endblock %}
    ''',

    'pedidos.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">{% if session.get('tipo') == 'vendedor' %}Minhas Vendas{% else %}Meus Pedidos{% endif %}</h2>
    <div style="background: #fff; padding: 60px 20px; text-align: center; border: 1px solid #f2ecdf; border-radius: 6px;">
        <p style="color: #a39686; font-size: 11pt; margin-bottom: 30px; font-style: italic;">Histórico de transações estará disponível após o primeiro pagamento.</p>
        <a href="/" class="btn-primary" style="text-decoration: none; padding: 15px 40px; display: inline-block; width: auto;">Explorar o Catálogo</a>
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
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        );
    ''')
    
    def add_column_if_not_exists(table, column, definition):
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND column_name='{column}';")
        if not cur.fetchone():
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition};")

    add_column_if_not_exists('usuarios', 'cpf', 'VARCHAR(20) UNIQUE')
    add_column_if_not_exists('usuarios', 'whatsapp', 'VARCHAR(20)')
    add_column_if_not_exists('usuarios', 'tipo', "VARCHAR(20) DEFAULT 'cliente'")
    add_column_if_not_exists('usuarios', 'aprovado', 'BOOLEAN DEFAULT TRUE')

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
    add_column_if_not_exists('produtos', 'custo', 'NUMERIC(10,2) DEFAULT 0')
    add_column_if_not_exists('produtos', 'imagem_base64', 'TEXT')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS entradas_estoque (
            id SERIAL PRIMARY KEY,
            produto_id INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
            quantidade INTEGER NOT NULL,
            custo_unitario NUMERIC(10,2) NOT NULL,
            data_compra DATE DEFAULT CURRENT_DATE
        );
    ''')

    cur.execute("UPDATE usuarios SET tipo = 'admin', aprovado = TRUE WHERE is_admin = TRUE;")
    cur.execute("SELECT COUNT(*) FROM usuarios WHERE tipo = 'admin';")
    if cur.fetchone()[0] == 0:
        senha_hash = generate_password_hash('admin123')
        cur.execute('''
            INSERT INTO usuarios (nome, email, senha, is_admin, tipo, aprovado)
            VALUES ('Admin Oliva', 'admin@oliva.com', %s, TRUE, 'admin', TRUE);
        ''', (senha_hash,))

    conn.commit()
    cur.close()
    conn.close()

try:
    init_db()
    print("Banco 100% Sincronizado: Acessos, Estoque e Fotos OK!")
except Exception as e:
    print(f"Aguardando banco... {e}")


# ==========================================
# 3. ROTAS DE SEGURANÇA E PROTEÇÃO
# ==========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Faça login ou crie uma conta para avançar.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or session.get('tipo') != 'admin':
            flash('Acesso bloqueado. Área restrita à diretoria.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# 4. ROTAS PÚBLICAS E CARRINHO
# ==========================================

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute('SELECT * FROM produtos WHERE estoque > 0 ORDER BY id DESC;')
        produtos = cur.fetchall()
    except:
        produtos = []
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
            try:
                cur.execute('SELECT id, nome, preco, volume_ml FROM produtos WHERE id = %s;', (id_produto,))
                produto = cur.fetchone()
                if produto:
                    produto['quantidade'] = qtd
                    produto['subtotal'] = float(produto['preco']) * qtd
                    total += produto['subtotal']
                    produtos_carrinho.append(produto)
            except:
                pass
        cur.close()
        conn.close()

    return render_template('carrinho.html', produtos=produtos_carrinho, total=total)

@app.route('/carrinho/adicionar/<int:id_produto>', methods=['POST'])
def adicionar_carrinho(id_produto):
    if 'carrinho' not in session: session['carrinho'] = {}
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

@app.route('/checkout')
@login_required
def checkout():
    flash('Módulo de pagamento será ativado na próxima fase!', 'success')
    return redirect(url_for('carrinho'))


# ==========================================
# 5. MÓDULO DE ACESSOS (LOGIN E CADASTRO)
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
            if not usuario['aprovado']:
                flash('Sua conta de revendedor ainda está em análise pela diretoria.', 'error')
                return redirect(url_for('login'))
                
            session['usuario_id'] = usuario['id']
            session['nome'] = usuario['nome']
            session['tipo'] = usuario['tipo']
            session['is_admin'] = usuario['is_admin']
            
            if usuario['tipo'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif usuario['tipo'] == 'vendedor':
                return redirect(url_for('index'))
            else:
                return redirect(url_for('carrinho'))
        else:
            flash('Credenciais inválidas.', 'error')
    return render_template('login.html')

@app.route('/cadastro/cliente', methods=['POST'])
def cadastro_cliente():
    nome = request.form['nome']
    email = request.form['email']
    whatsapp = request.form['whatsapp']
    senha = generate_password_hash(request.form['senha'])
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO usuarios (nome, email, whatsapp, senha, tipo, aprovado)
            VALUES (%s, %s, %s, %s, 'cliente', TRUE) RETURNING id;
        ''', (nome, email, whatsapp, senha))
        novo_id = cur.fetchone()[0]
        conn.commit()
        session['usuario_id'] = novo_id
        session['nome'] = nome
        session['tipo'] = 'cliente'
        flash('Conta criada com sucesso! Pode finalizar seu pedido.', 'success')
        return redirect(url_for('carrinho'))
    except psycopg2.errors.UniqueViolation:
        flash('Este e-mail ou CPF já está cadastrado.', 'error')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('login'))

@app.route('/seja-revendedor', methods=['GET'])
def pagina_revendedor():
    return render_template('revendedor.html')

@app.route('/cadastro/revendedor', methods=['POST'])
def cadastro_revendedor():
    nome = request.form['nome']
    cpf = request.form['cpf']
    email = request.form['email']
    whatsapp = request.form['whatsapp']
    senha = generate_password_hash(request.form['senha'])
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO usuarios (nome, cpf, email, whatsapp, senha, tipo, aprovado)
            VALUES (%s, %s, %s, %s, %s, 'vendedor', FALSE);
        ''', (nome, cpf, email, whatsapp, senha))
        conn.commit()
        flash('Solicitação enviada! Aguarde a aprovação da nossa equipe pelo WhatsApp.', 'success')
    except psycopg2.errors.UniqueViolation:
        flash('Este e-mail ou CPF já possui cadastro no sistema.', 'error')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com segurança.', 'success')
    return redirect(url_for('index'))

@app.route('/meus-pedidos')
@login_required
def meus_pedidos():
    return render_template('pedidos.html')


# ==========================================
# 6. ROTAS GERENCIAIS (ADMIN TOTAL)
# ==========================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT COUNT(*) FROM produtos;')
        total_produtos = cur.fetchone()[0]
        cur.execute('SELECT SUM(estoque) FROM produtos;')
        estoque_total = cur.fetchone()[0] or 0
    except:
        total_produtos, estoque_total = 0, 0
    cur.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='vendedor' AND aprovado=FALSE;")
    pendentes = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('admin.html', total_produtos=total_produtos, estoque_total=estoque_total, pendentes=pendentes)

@app.route('/admin/aprovacoes')
@admin_required
def admin_aprovacoes():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM usuarios WHERE tipo='vendedor' AND aprovado=FALSE ORDER BY id DESC;")
    revendedores = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin_aprovacoes.html', revendedores=revendedores)

@app.route('/admin/aprovar/<int:id>', methods=['POST'])
@admin_required
def aprovar_revendedor(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios SET aprovado = TRUE WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Conta de revendedor ativada com sucesso!', 'success')
    return redirect(url_for('admin_aprovacoes'))

@app.route('/admin/estoque', methods=['GET', 'POST'])
@admin_required
def admin_estoque():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'novo_produto':
            nome = request.form['nome']
            volume_ml = request.form['volume_ml']
            preco = request.form['preco']
            custo = request.form['custo']
            estoque_inicial = int(request.form['estoque'])
            descricao = request.form.get('descricao', '')
            
            imagem_file = request.files.get('imagem')
            imagem_b64 = None
            if imagem_file and imagem_file.filename != '':
                imagem_b64 = base64.b64encode(imagem_file.read()).decode('utf-8')
            
            cur.execute('''
                INSERT INTO produtos (nome, descricao, preco, custo, volume_ml, estoque, imagem_base64)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
            ''', (nome, descricao, preco, custo, volume_ml, estoque_inicial, imagem_b64))
            novo_produto_id = cur.fetchone()['id']
            
            if estoque_inicial > 0:
                cur.execute('''
                    INSERT INTO entradas_estoque (produto_id, quantidade, custo_unitario, data_compra)
                    VALUES (%s, %s, %s, CURRENT_DATE);
                ''', (novo_produto_id, estoque_inicial, custo))
            flash(f'{nome} adicionado ao catálogo!', 'success')
            
        elif action == 'nova_entrada':
            produto_id = request.form['produto_id']
            quantidade = int(request.form['quantidade'])
            custo = request.form['custo']
            data_compra = request.form['data_compra']
            
            cur.execute('''
                INSERT INTO entradas_estoque (produto_id, quantidade, custo_unitario, data_compra)
                VALUES (%s, %s, %s, %s);
            ''', (produto_id, quantidade, custo, data_compra))
            cur.execute('UPDATE produtos SET estoque = estoque + %s, custo = %s WHERE id = %s;', (quantidade, custo, produto_id))
            flash('Reposição registrada com sucesso!', 'success')

        conn.commit()
        return redirect(url_for('admin_estoque'))
    
    data_hoje = datetime.today().strftime('%Y-%m-%d')
    cur.execute('SELECT * FROM produtos ORDER BY id DESC;')
    produtos = cur.fetchall()
    cur.execute('''
        SELECT e.quantidade, e.custo_unitario, TO_CHAR(e.data_compra, 'DD/MM/YYYY') as data_formatada, p.nome 
        FROM entradas_estoque e JOIN produtos p ON e.produto_id = p.id ORDER BY e.data_compra DESC, e.id DESC;
    ''')
    entradas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('estoque.html', produtos=produtos, entradas=entradas, data_hoje=data_hoje)

@app.route('/admin/produto/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_editar_produto(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        nome = request.form['nome']
        volume_ml = request.form['volume_ml']
        preco = request.form['preco']
        custo = request.form['custo']
        descricao = request.form.get('descricao', '')
        imagem_file = request.files.get('imagem')
        
        if imagem_file and imagem_file.filename != '':
            imagem_b64 = base64.b64encode(imagem_file.read()).decode('utf-8')
            cur.execute('''
                UPDATE produtos SET nome=%s, volume_ml=%s, preco=%s, custo=%s, descricao=%s, imagem_base64=%s WHERE id=%s
            ''', (nome, volume_ml, preco, custo, descricao, imagem_b64, id))
        else:
            cur.execute('''
                UPDATE produtos SET nome=%s, volume_ml=%s, preco=%s, custo=%s, descricao=%s WHERE id=%s
            ''', (nome, volume_ml, preco, custo, descricao, id))
            
        conn.commit()
        cur.close()
        conn.close()
        flash('Fragrância atualizada com sucesso no sistema!', 'success')
        return redirect(url_for('admin_estoque'))
        
    cur.execute('SELECT * FROM produtos WHERE id = %s', (id,))
    produto = cur.fetchone()
    cur.close()
    conn.close()
    if not produto:
        return redirect(url_for('admin_estoque'))
    return render_template('editar_produto.html', p=produto)

@app.route('/admin/comissao')
def admin_comissao():
    if 'usuario_id' not in session or session.get('tipo') == 'cliente':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT id, nome, preco, custo, volume_ml FROM produtos ORDER BY preco DESC;')
    produtos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('comissao.html', produtos=produtos)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
