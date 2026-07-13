import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jinja2
from datetime import datetime
import base64
import requests

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
            body { background-color: #fcfaf7; color: #332d27; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 300; -webkit-font-smoothing: antialiased; display: flex; flex-direction: column; min-height: 100vh; }
            
            .navbar { background-color: transparent; padding: 25px 0; border-bottom: 1px solid #eae1d3; }
            .nav-container { max-width: 1100px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; width: 100%; }
            .logo-text { font-family: 'Times New Roman', Georgia, serif; font-size: 26pt; color: #b89758; text-decoration: none; letter-spacing: 8px; text-transform: uppercase; }
            .navbar nav { display: flex; flex-wrap: wrap; align-items: center; justify-content: flex-end; }
            .navbar nav a { color: #665b4f; text-decoration: none; margin-left: 20px; font-size: 9.5pt; letter-spacing: 1px; text-transform: uppercase; transition: color 0.3s; font-weight: 500; }
            .navbar nav a:hover { color: #b89758; }
            
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
            
            .dashboard-cards { display: flex; gap: 20px; margin-bottom: 40px; flex-wrap: wrap; }
            .card { background: #ffffff; padding: 30px; border: 1px solid #eae1d3; border-top: 3px solid #b89758; flex: 1; min-width: 200px; border-radius: 6px; text-align: center; }
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
            .btn-secondary { background-color: transparent; color: #665b4f; border: 1px solid #dfd5c6; padding: 14px 20px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; text-transform: uppercase; font-size: 9pt; text-align: center; transition: all 0.3s;}
            .btn-secondary:hover { background-color: #f2ecdf; }
            
            .alert { padding: 15px; margin-bottom: 25px; border-radius: 4px; background-color: #fdfbf7; border-left: 4px solid #b89758; color: #665b4f; font-size: 10pt; width: 100%; }
            .alert-error { border-left-color: #d9534f; color: #d9534f; background-color: #fff0f0; }
            .alert-info { border-left-color: #31708f; color: #31708f; background-color: #d9edf7; }
            
            .table-wrapper { width: 100%; overflow-x: auto; margin-bottom: 30px; border-radius: 6px; background: #fff; border: 1px solid #f2ecdf; }
            table { width: 100%; border-collapse: collapse; min-width: 600px; }
            th, td { padding: 16px 15px; text-align: left; border-bottom: 1px solid #f2ecdf; white-space: nowrap; }
            th { background-color: #fffcf7; color: #8c764d; font-size: 9pt; text-transform: uppercase; font-weight: 500; }
            
            .badge { padding: 5px 10px; border-radius: 4px; font-size: 8.5pt; font-weight: bold; text-transform: uppercase; }
            .badge-green { background: #eefaf2; color: #3c763d; border: 1px solid #4cae4c; }
            .badge-yellow { background: #fff8e1; color: #8a6d3b; border: 1px solid #faebcc; }
            .badge-gray { background: #f5f5f5; color: #666; border: 1px solid #ccc; }
            
            .main-footer { text-align: center; padding: 40px 0; margin-top: auto; font-size: 9pt; color: #a39686; border-top: 1px solid #eae1d3; letter-spacing: 1px; width: 100%; background-color: #fcfaf7; }
            
            @media (max-width: 768px) {
                .nav-container { flex-direction: column; gap: 15px; text-align: center; }
                .navbar nav { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; }
                .navbar nav a { margin: 0 5px; font-size: 8pt; }
                .product-card { width: 48%; }
                .col-50 { width: 100%; }
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
                            <a href="/admin/comissao">Vendas & Pedidos</a>
                            <a href="/admin/usuarios">Usuários</a>
                            <a href="/admin/configuracoes">⚙️ API</a>
                        {% elif session.get('tipo') == 'vendedor' %}
                            <a href="/carrinho">Carrinho</a>
                            <a href="/vendedor/painel">Minhas Vendas & Link</a>
                        {% else %}
                            <a href="/carrinho">Carrinho</a>
                            <a href="/meus-pedidos">Meus Pedidos</a>
                        {% endif %}
                        <a href="/logout" style="color: #d9534f; font-weight: bold;">Sair</a>
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
                        <div class="alert {% if category == 'error' %}alert-error{% elif category == 'info' %}alert-info{% endif %}">{{ message }}</div>
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
        {% if session.get('vendedor_id_ref') %}
            <div style="margin-top: 15px; display: inline-block; padding: 5px 15px; background: #fdfbf7; border: 1px solid #b89758; border-radius: 20px; font-size: 9pt; color: #8c764d;">
                ✨ Você está comprando através de um Consultor Oficial OLIVA.
            </div>
        {% endif %}
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
                    <button type="submit" class="btn-primary">Adicionar ao Carrinho</button>
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
            <a href="/checkout" class="btn-primary" style="max-width: 300px; text-align: center; text-decoration: none; box-sizing: border-box; background-color: #2c2621; color: #b89758;">Finalizar Pagamento (PIX/Cartão)</a>
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
            <h3>Faturamento Total</h3>
            <p style="color: #3c763d; font-size: 20pt;">R$ {{ "%.2f"|format(faturamento) }}</p>
        </div>
        <div class="card">
            <h3>Fragrâncias Ativas</h3>
            <p>{{ total_produtos }}</p>
        </div>
        <div class="card">
            <h3>Pedidos Concluídos</h3>
            <p>{{ total_pedidos }}</p>
        </div>
        <div class="card">
            <h3>Aprovações Pendentes</h3>
            <p style="color: #d9534f;">{{ pendentes }}</p>
        </div>
    </div>
    {% endblock %}
    ''',

    'admin_usuarios.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Gestão de Usuários</h2>
    <div class="table-wrapper">
        <table>
            <tr><th>ID</th><th>Nome / Contato</th><th>Tipo</th><th>Status</th><th>Ação</th></tr>
            {% for u in usuarios %}
            <tr>
                <td style="color: #a39686;">#{{ u.id }}</td>
                <td style="color: #2c2621; font-weight: 500;">
                    {{ u.nome }}<br>
                    <span style="font-size: 8.5pt; color: #8c764d; font-weight: normal;">{{ u.email }} | {{ u.whatsapp or 'S/ Whats' }}</span>
                </td>
                <td><span class="badge {% if u.tipo == 'admin' %}badge-yellow{% elif u.tipo == 'vendedor' %}badge-green{% else %}badge-default{% endif %}">{{ u.tipo }}</span></td>
                <td>{% if u.aprovado %}✔️ Aprovado{% else %}⏳ Pendente{% endif %}</td>
                <td>
                    <div style="display: flex; gap: 10px;">
                        <a href="/admin/usuario/editar/{{ u.id }}" style="color: #b89758; text-decoration: none; font-size: 8pt; font-weight: bold; text-transform: uppercase;">Editar</a>
                        {% if u.id != session.usuario_id %}
                        <a href="/admin/usuario/excluir/{{ u.id }}" style="color: #d9534f; text-decoration: none; font-size: 8pt; font-weight: bold; text-transform: uppercase;" onclick="return confirm('Certeza que deseja excluir este usuário?');">Excluir</a>
                        {% endif %}
                    </div>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endblock %}
    ''',

    'admin_editar_usuario.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Editar Usuário: {{ u.nome }}</h2>
    <div style="background: #fff; padding: 40px; border: 1px solid #f2ecdf; border-radius: 6px; max-width: 600px; margin: 0 auto;">
        <form method="POST" action="/admin/usuario/editar/{{ u.id }}" class="form-row">
            <div class="form-group col-100"><label>Nome Completo</label><input type="text" name="nome" required value="{{ u.nome }}"></div>
            <div class="form-group col-100"><label>E-mail</label><input type="email" name="email" required value="{{ u.email }}"></div>
            <div class="form-group col-50"><label>WhatsApp</label><input type="text" name="whatsapp" value="{{ u.whatsapp or '' }}"></div>
            <div class="form-group col-50"><label>CPF</label><input type="text" name="cpf" value="{{ u.cpf or '' }}"></div>
            <div class="form-group col-50">
                <label>Tipo de Conta</label>
                <select name="tipo">
                    <option value="cliente" {% if u.tipo == 'cliente' %}selected{% endif %}>Cliente</option>
                    <option value="vendedor" {% if u.tipo == 'vendedor' %}selected{% endif %}>Vendedor(a)</option>
                    <option value="admin" {% if u.tipo == 'admin' %}selected{% endif %}>Administrador</option>
                </select>
            </div>
            <div class="form-group col-50">
                <label>Status de Aprovação</label>
                <select name="aprovado">
                    <option value="1" {% if u.aprovado %}selected{% endif %}>Aprovado / Liberado</option>
                    <option value="0" {% if not u.aprovado %}selected{% endif %}>Bloqueado / Pendente</option>
                </select>
            </div>
            <div class="col-100" style="display: flex; gap: 15px; margin-top: 20px;">
                <button type="submit" class="btn-primary">Salvar Alterações</button>
                <a href="/admin/usuarios" class="btn-secondary">Voltar</a>
            </div>
        </form>
    </div>
    {% endblock %}
    ''',

    'admin_config.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Integração de Pagamento</h2>
    <div style="background: #fff; padding: 40px; border: 1px solid #f2ecdf; border-radius: 6px; max-width: 800px; margin: 0 auto;">
        <h3 style="color: #2c2621; margin-bottom: 15px;">API do Mercado Pago</h3>
        <p style="font-size: 10pt; color: #666; margin-bottom: 30px;">
            Para que o site receba pagamentos reais em PIX e Cartão via Mercado Pago, você precisa colar o seu <strong>Access Token (Produção)</strong> abaixo.
        </p>
        <form method="POST" action="/admin/configuracoes">
            <div class="form-group">
                <label>Mercado Pago: Access Token</label>
                <input type="password" name="mp_access_token" value="{{ mp_token }}" placeholder="APP_USR-123456789..." required>
                <p style="font-size: 8.5pt; color: #8c764d; margin-top: 8px;">Deixe salvo para ativar o botão de checkout no carrinho.</p>
            </div>
            <button type="submit" class="btn-primary" style="width: auto; padding: 12px 40px;">Salvar Integração</button>
        </form>
    </div>
    {% endblock %}
    ''',

    'admin_comissao.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Gestão de Vendas & Comissões</h2>
    <div class="alert alert-info">
        Aqui você gerencia todos os pedidos realizados. É por aqui que você sabe o que separar no estoque e qual comissão pagar.
    </div>
    <div class="table-wrapper">
        <table>
            <tr><th>Data / Pedido</th><th>Itens Vendidos</th><th>Vendedor(a)</th><th>Cliente</th><th>Total</th><th>Comissão (10%)</th><th>Status Pago</th></tr>
            {% for v in vendas %}
            <tr>
                <td style="color: #a39686; font-size: 9pt;">{{ v.data_formatada }}<br><span style="color:#2c2621; font-weight:bold; font-size: 11pt;">#{{ v.id }}</span></td>
                <td style="color: #666; font-size: 9pt; line-height: 1.5;">
                    {% for item in v.itens %}
                        <strong>{{ item.quantidade }}x</strong> {{ item.nome }} ({{ item.volume_ml }}ml)<br>
                    {% endfor %}
                </td>
                <td style="color: #2c2621; font-weight: bold;">{{ v.vendedor_nome or 'Venda Direta (S/ Ref)' }}</td>
                <td style="color: #666;">{{ v.cliente_nome }}</td>
                <td style="font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(v.valor_total) }}</td>
                <td style="color: #b89758; font-weight: bold; font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(v.comissao_total) }}</td>
                <td>
                    {% if v.status_pagamento != 'aprovado' %}
                        <span class="badge badge-yellow">Aguardando Pagamento</span>
                    {% else %}
                        {% if v.vendedor_nome %}
                            {% if v.status_comissao == 'paga' %}
                                <span class="badge badge-green">Comissão Paga</span>
                            {% else %}
                                <form action="/admin/comissao/pagar/{{ v.id }}" method="POST" style="display:inline;">
                                    <button type="submit" class="btn-primary" style="padding: 6px 12px; font-size: 8pt; width: auto; background-color: #d9534f;">Marcar Paga</button>
                                </form>
                            {% endif %}
                        {% else %}
                            <span class="badge badge-green">100% da Loja</span>
                        {% endif %}
                    {% endif %}
                </td>
            </tr>
            {% else %}
            <tr><td colspan="7" style="text-align: center; padding: 30px; color: #a39686;">Nenhuma venda registrada ainda.</td></tr>
            {% endfor %}
        </table>
    </div>
    {% endblock %}
    ''',

    'vendedor_painel.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Meu Painel de Vendas</h2>
    
    <div style="background: #fdfbf7; border: 2px dashed #b89758; padding: 25px; border-radius: 6px; text-align: center; margin-bottom: 40px;">
        <h3 style="color: #2c2621; margin-bottom: 10px;">Seu Link Exclusivo de Vendas</h3>
        <p style="color: #666; font-size: 10pt; margin-bottom: 15px;">Copie o link abaixo e envie para seus clientes. Toda compra gerada por ele vai direto para sua conta!</p>
        <input type="text" readonly value="{{ host_url }}/?ref={{ session.usuario_id }}" style="text-align: center; font-weight: bold; color: #b89758; background: #fff; max-width: 500px; margin: 0 auto; display: block;">
    </div>

    <div class="dashboard-cards">
        <div class="card">
            <h3>Minhas Vendas (R$)</h3>
            <p>R$ {{ "%.2f"|format(total_vendas) }}</p>
        </div>
        <div class="card">
            <h3>Comissões Pendentes</h3>
            <p style="color: #d9534f;">R$ {{ "%.2f"|format(comissao_pendente) }}</p>
        </div>
        <div class="card">
            <h3>Comissões Recebidas</h3>
            <p style="color: #3c763d;">R$ {{ "%.2f"|format(comissao_paga) }}</p>
        </div>
    </div>

    <h3 style="margin-bottom: 15px; color: #2c2621; font-family: 'Times New Roman', serif; font-size: 16pt;">Extrato de Pedidos dos Seus Clientes</h3>
    <div class="table-wrapper">
        <table>
            <tr><th>Data / Pedido</th><th>Itens Comprados</th><th>Cliente</th><th>Valor Vendido</th><th>Sua Comissão</th><th>Status Repasse</th></tr>
            {% for v in vendas %}
            <tr>
                <td style="color: #a39686; font-size: 9pt;">{{ v.data_formatada }}<br><span style="color:#2c2621; font-weight:bold; font-size:11pt;">#{{ v.id }}</span></td>
                <td style="color: #666; font-size: 9pt; line-height: 1.5;">
                    {% for item in v.itens %}
                        <strong>{{ item.quantidade }}x</strong> {{ item.nome }} ({{ item.volume_ml }}ml)<br>
                    {% endfor %}
                </td>
                <td style="color: #2c2621; font-weight: 500;">{{ v.cliente_nome }}</td>
                <td style="font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(v.valor_total) }}</td>
                <td style="color: #b89758; font-weight: bold; font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(v.comissao_total) }}</td>
                <td>
                    {% if v.status_comissao == 'paga' %}
                        <span class="badge badge-green">Paga pela OLIVA</span>
                    {% else %}
                        <span class="badge badge-yellow">Aguardando Repasse</span>
                    {% endif %}
                </td>
            </tr>
            {% else %}
            <tr><td colspan="6" style="text-align: center; color: #a39686; font-style: italic; padding: 20px;">Você ainda não realizou vendas faturadas.</td></tr>
            {% endfor %}
        </table>
    </div>
    {% endblock %}
    ''',

    'pedidos_cliente.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Meus Pedidos</h2>
    {% if pedidos %}
        <div class="table-wrapper">
            <table>
                <tr><th>Pedido</th><th>Itens Comprados</th><th>Data da Compra</th><th>Valor Total</th><th>Status do Pagamento</th></tr>
                {% for p in pedidos %}
                <tr>
                    <td style="color: #2c2621; font-weight: 500; font-size: 11pt;">#{{ p.id }}</td>
                    <td style="color: #666; font-size: 9pt; line-height: 1.5;">
                        {% for item in p.itens %}
                            <strong>{{ item.quantidade }}x</strong> {{ item.nome }} ({{ item.volume_ml }}ml)<br>
                        {% endfor %}
                    </td>
                    <td style="color: #666;">{{ p.data_formatada }}</td>
                    <td style="font-family: 'Times New Roman', serif; font-size: 12pt;">R$ {{ "%.2f"|format(p.valor_total) }}</td>
                    <td>
                        {% if p.status_pagamento == 'aprovado' %}
                            <span class="badge badge-green">Pagamento Aprovado</span>
                        {% elif p.status_pagamento == 'in_process' or p.status_pagamento == 'em_analise' %}
                            <span class="badge badge-yellow" style="background: #eef8ff; color: #31708f; border-color: #bce8f1;">Em Análise pelo Banco</span>
                        {% else %}
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <span class="badge badge-yellow">Aguardando Pagamento</span>
                                {% if p.mp_preference_id %}
                                    <a href="https://www.mercadopago.com.br/checkout/v1/redirect?pref_id={{ p.mp_preference_id }}" class="btn-primary" style="padding: 8px 20px; font-size: 8pt; width: auto; text-decoration: none; margin: 0; background-color: #2c2621; color: #b89758;">💳 Pagar Agora</a>
                                {% else %}
                                    <span class="badge badge-gray">Link Inválido (Erro)</span>
                                {% endif %}
                            </div>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    {% else %}
        <div style="background: #fff; padding: 60px 20px; text-align: center; border: 1px solid #f2ecdf; border-radius: 6px;">
            <p style="color: #a39686; font-size: 11pt; margin-bottom: 30px; font-style: italic;">Você ainda não possui pedidos registrados.</p>
            <a href="/" class="btn-primary" style="text-decoration: none; padding: 15px 40px; display: inline-block; width: auto;">Explorar o Catálogo</a>
        </div>
    {% endif %}
    {% endblock %}
    ''',
    
    'estoque.html': '''{% extends 'base.html' %}{% block content %}<h2 class="page-title">Gestão de Estoque</h2><div style="display: flex; flex-direction: column; gap: 30px; margin-bottom: 50px;"><div style="background: #fff; padding: 30px 20px; border: 1px solid #f2ecdf; border-radius: 6px;"><h3 style="margin-bottom: 20px; color: #2c2621; font-family: 'Times New Roman', serif; font-size: 15pt;">1. Cadastrar Novo Decant</h3><form method="POST" action="/admin/estoque" enctype="multipart/form-data" class="form-row"><input type="hidden" name="action" value="novo_produto"><div class="form-group col-100"><label>Nome do Perfume</label><input type="text" name="nome" required></div><div class="form-group col-50"><label>Volumetria (ml)</label><input type="number" name="volume_ml" required></div><div class="form-group col-50"><label>Estoque Inicial</label><input type="number" name="estoque" required value="0"></div><div class="form-group col-50"><label>Custo Pago (R$)</label><input type="number" step="0.01" name="custo" required placeholder="0.00"></div><div class="form-group col-50"><label>Preço Venda (R$)</label><input type="number" step="0.01" name="preco" required placeholder="0.00"></div><div class="form-group col-100"><label>Foto do Produto</label><input type="file" name="imagem" accept="image/*"></div><div class="form-group col-100"><label>Descrição Olfativa</label><textarea name="descricao" rows="2"></textarea></div><div class="col-100"><button type="submit" class="btn-primary">Criar Cadastro</button></div></form></div><div style="background: #fff; padding: 30px 20px; border: 1px solid #f2ecdf; border-radius: 6px;"><h3 style="margin-bottom: 20px; color: #2c2621; font-family: 'Times New Roman', serif; font-size: 15pt;">2. Registrar Reposição</h3><form method="POST" action="/admin/estoque" class="form-row"><input type="hidden" name="action" value="nova_entrada"><div class="form-group col-100"><label>Selecione a Fragrância</label><select name="produto_id" required><option value="">-- Escolha --</option>{% for p in produtos %}<option value="{{ p.id }}">{{ p.nome }} ({{ p.volume_ml }}ml)</option>{% endfor %}</select></div><div class="form-group col-100"><label>Data da Compra</label><input type="date" name="data_compra" required value="{{ data_hoje }}"></div><div class="form-group col-50"><label>Qtd Comprada</label><input type="number" name="quantidade" required min="1"></div><div class="form-group col-50"><label>Custo Unitário (R$)</label><input type="number" step="0.01" name="custo" required></div><div class="col-100"><button type="submit" class="btn-primary" style="background-color: #2c2621; color: #b89758;">Gravar Estoque</button></div></form></div></div><h3 style="margin-bottom: 15px; color: #2c2621; font-family: 'Times New Roman', serif; font-size: 15pt;">Catálogo Atual & Edição</h3><div class="table-wrapper"><table><tr><th>Foto</th><th>Fragrância</th><th>Custo</th><th>Venda</th><th>Estoque</th><th>Ação</th></tr>{% for p in produtos %}<tr><td>{% if p.imagem_base64 %}<img src="data:image/jpeg;base64,{{ p.imagem_base64 }}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #eae1d3;">{% else %}<div style="width: 40px; height: 40px; background: #fcfaf7; border: 1px solid #eae1d3; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 8pt; color: #b89758;">✧</div>{% endif %}</td><td style="color: #2c2621; font-weight: 500; white-space: normal; min-width: 150px;">{{ p.nome }} <span style="color: #8c764d; font-size: 9pt;">({{ p.volume_ml }}ml)</span></td><td style="color: #666; font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(p.custo) if p.custo else "0.00" }}</td><td style="font-family: 'Times New Roman', serif; color: #2c2621; font-weight: bold;">R$ {{ "%.2f"|format(p.preco) }}</td><td><span style="padding: 4px 10px; background: {% if p.estoque < 5 %}#fffcf7{% else %}transparent{% endif %}; border: 1px solid {% if p.estoque < 5 %}#b89758{% else %}#eae1d3{% endif %}; border-radius: 4px; font-size: 9pt; color: #665b4f;">{{ p.estoque }} un</span></td><td><a href="/admin/produto/editar/{{ p.id }}" style="color: #b89758; text-decoration: none; font-size: 9pt; text-transform: uppercase; font-weight: bold;">Editar</a></td></tr>{% endfor %}</table></div>{% endblock %}''',
    'editar_produto.html': '''{% extends 'base.html' %}{% block content %}<h2 class="page-title">Editar Fragrância</h2><div style="background: #fff; padding: 30px 20px; border: 1px solid #f2ecdf; border-radius: 6px; margin-bottom: 30px;"><form method="POST" action="/admin/produto/editar/{{ p.id }}" enctype="multipart/form-data" class="form-row"><div class="form-group col-100"><label>Nome do Perfume</label><input type="text" name="nome" required value="{{ p.nome }}"></div><div class="form-group col-50"><label>Volumetria (ml)</label><input type="number" name="volume_ml" required value="{{ p.volume_ml }}"></div><div class="form-group col-50"><label>Custo Base Atual (R$)</label><input type="number" step="0.01" name="custo" required value="{{ p.custo }}"></div><div class="form-group col-100"><label>Preço Venda (R$)</label><input type="number" step="0.01" name="preco" required value="{{ p.preco }}"></div><div class="form-group col-100"><label>Nova Foto (Deixe em branco para manter a atual)</label><input type="file" name="imagem" accept="image/*"></div><div class="form-group col-100"><label>Descrição Olfativa</label><textarea name="descricao" rows="4">{{ p.descricao }}</textarea></div><div class="col-100" style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;"><button type="submit" class="btn-primary">Salvar Alterações</button><a href="/admin/estoque" class="btn-secondary">Voltar sem Salvar</a></div></form></div>{% endblock %}''',
    'admin_aprovacoes.html': '''{% extends 'base.html' %}{% block content %}<h2 class="page-title">Aprovação de Revendedores</h2><div class="alert" style="background: #fff; border-left-color: #2c2621;">Gerencie as contas que solicitaram acesso ao programa de comissões e vendas exclusivas.</div><div class="table-wrapper"><table><tr><th>Data</th><th>Nome</th><th>CPF / WhatsApp</th><th>Email</th><th>Ação</th></tr>{% for v in revendedores %}<tr><td style="color: #a39686;">#{{ v.id }}</td><td style="color: #2c2621; font-weight: 500;">{{ v.nome }}</td><td style="color: #666;">{{ v.cpf }}<br><span style="font-size: 9pt;">{{ v.whatsapp }}</span></td><td>{{ v.email }}</td><td><form action="/admin/aprovar/{{ v.id }}" method="POST" style="display:inline;"><button type="submit" class="btn-primary" style="padding: 8px 15px; width: auto; font-size: 8pt;">Aprovar</button></form></td></tr>{% else %}<tr><td colspan="5" style="text-align: center; color: #a39686; font-style: italic;">Nenhuma solicitação pendente.</td></tr>{% endfor %}</table></div>{% endblock %}'''
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
            is_admin BOOLEAN DEFAULT FALSE,
            cpf VARCHAR(20) UNIQUE,
            whatsapp VARCHAR(20),
            tipo VARCHAR(20) DEFAULT 'cliente',
            aprovado BOOLEAN DEFAULT TRUE
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
            imagem_url VARCHAR(255),
            custo NUMERIC(10,2) DEFAULT 0,
            imagem_base64 TEXT
        );
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS entradas_estoque (
            id SERIAL PRIMARY KEY,
            produto_id INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
            quantidade INTEGER NOT NULL,
            custo_unitario NUMERIC(10,2) NOT NULL,
            data_compra DATE DEFAULT CURRENT_DATE
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id SERIAL PRIMARY KEY,
            chave VARCHAR(50) UNIQUE NOT NULL,
            valor TEXT
        );
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            vendedor_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            valor_total NUMERIC(10,2) NOT NULL,
            comissao_total NUMERIC(10,2) DEFAULT 0,
            status_pagamento VARCHAR(50) DEFAULT 'pendente',
            status_comissao VARCHAR(50) DEFAULT 'pendente',
            mp_preference_id VARCHAR(100),
            data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
            produto_id INTEGER REFERENCES produtos(id) ON DELETE SET NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario NUMERIC(10,2) NOT NULL
        );
    ''')

    cur.execute("INSERT INTO configuracoes (chave, valor) VALUES ('mp_access_token', '') ON CONFLICT DO NOTHING;")

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
    print("Banco atualizado!")
except Exception as e:
    print(f"Erro no banco: {e}")

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
    ref = request.args.get('ref')
    if ref:
        session['vendedor_id_ref'] = int(ref)
        
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
        for id_produto_str, qtd in carrinho_itens.items():
            cur.execute('SELECT id, nome, preco, volume_ml FROM produtos WHERE id = %s;', (int(id_produto_str),))
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
    carrinho = dict(session.get('carrinho', {}))
    id_str = str(id_produto)
    carrinho[id_str] = carrinho.get(id_str, 0) + 1
    session['carrinho'] = carrinho
    session.modified = True
    
    flash("Fragrância adicionada ao carrinho!", "success")
    return redirect(url_for('index'))

@app.route('/carrinho/limpar')
def limpar_carrinho():
    session.pop('carrinho', None)
    return redirect(url_for('carrinho'))

# --- INTEGRAÇÃO MERCADO PAGO ---
@app.route('/checkout')
@login_required
def checkout():
    carrinho_itens = session.get('carrinho', {})
    if not carrinho_itens:
        flash('Seu carrinho está vazio.', 'error')
        return redirect(url_for('carrinho'))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT valor FROM configuracoes WHERE chave='mp_access_token'")
    token_row = cur.fetchone()
    if not token_row or not token_row['valor'] or token_row['valor'].strip() == '':
        flash('O administrador do site ainda não configurou o gateway de pagamento.', 'error')
        cur.close(); conn.close()
        return redirect(url_for('carrinho'))
    
    mp_token = token_row['valor'].strip()
    valor_total = 0.0
    itens_para_banco = []
    
    for id_produto_str, qtd in carrinho_itens.items():
        cur.execute('SELECT preco FROM produtos WHERE id = %s;', (int(id_produto_str),))
        p = cur.fetchone()
        if p:
            preco_unitario = float(p['preco'])
            valor_total += preco_unitario * qtd
            itens_para_banco.append((int(id_produto_str), qtd, preco_unitario))
            
    comissao_total = valor_total * 0.10
    vendedor_id = session.get('vendedor_id_ref')

    cur.execute('''
        INSERT INTO pedidos (cliente_id, vendedor_id, valor_total, comissao_total)
        VALUES (%s, %s, %s, %s) RETURNING id;
    ''', (session['usuario_id'], vendedor_id, valor_total, comissao_total))
    pedido_id = cur.fetchone()['id']
    
    for id_produto, qtd, preco in itens_para_banco:
        cur.execute('''
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
            VALUES (%s, %s, %s, %s);
        ''', (pedido_id, id_produto, qtd, preco))
        
    conn.commit()
    
    host_url = request.url_root.rstrip('/')
    if host_url.startswith('http://') and 'localhost' not in host_url and '127.0.0.1' not in host_url:
        host_url = host_url.replace('http://', 'https://')
        
    headers = {"Authorization": f"Bearer {mp_token}", "Content-Type": "application/json"}
    payload = {
        "items": [
            {
                "title": f"Pedido #{pedido_id} - OLIVA Decants",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(valor_total)
            }
        ],
        "back_urls": {
            "success": f"{host_url}/pagamento/sucesso/{pedido_id}",
            "failure": f"{host_url}/meus-pedidos",
            "pending": f"{host_url}/meus-pedidos"
        },
        "auto_return": "approved",
        "external_reference": str(pedido_id)
    }
    
    try:
        response = requests.post("https://api.mercadopago.com/checkout/preferences", json=payload, headers=headers)
        if response.status_code in [200, 201]:
            init_point = response.json()['init_point']
            cur.execute("UPDATE pedidos SET mp_preference_id = %s WHERE id = %s", (response.json()['id'], pedido_id))
            conn.commit()
            
            session.pop('carrinho', None)
            cur.close(); conn.close()
            return redirect(init_point)
        else:
            erro_mp = response.json().get('message', 'Configuração de Token ou URL inválida.')
            cur.close(); conn.close()
            flash(f'Falha na integração MP: {erro_mp}', 'error')
            return redirect(url_for('carrinho'))
    except Exception as e:
        cur.close(); conn.close()
        flash('O sistema está sem acesso externo no momento.', 'error')
        return redirect(url_for('carrinho'))

@app.route('/pagamento/sucesso/<int:pedido_id>')
@login_required
def pagamento_sucesso(pedido_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE pedidos SET status_pagamento = 'aprovado' WHERE id = %s", (pedido_id,))
    cur.execute("SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = %s", (pedido_id,))
    itens = cur.fetchall()
    for item in itens:
        cur.execute("UPDATE produtos SET estoque = estoque - %s WHERE id = %s", (item[1], item[0]))
    conn.commit()
    cur.close(); conn.close()
    
    flash('Pagamento Aprovado! Seu pedido já está sendo preparado.', 'success')
    return redirect(url_for('meus_pedidos'))

# ==========================================
# 5. MÓDULO DE ACESSOS E PAINEL DO VENDEDOR
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
                flash('Sua conta está em análise.', 'error')
                return redirect(url_for('login'))
                
            session['usuario_id'] = usuario['id']
            session['nome'] = usuario['nome']
            session['tipo'] = usuario['tipo']
            session['is_admin'] = usuario['is_admin']
            
            if usuario['tipo'] == 'admin': return redirect(url_for('admin_dashboard'))
            elif usuario['tipo'] == 'vendedor': return redirect(url_for('vendedor_painel'))
            else: return redirect(url_for('carrinho'))
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
        cur.execute('''INSERT INTO usuarios (nome, email, whatsapp, senha, tipo, aprovado) VALUES (%s, %s, %s, %s, 'cliente', TRUE) RETURNING id;''', (nome, email, whatsapp, senha))
        novo_id = cur.fetchone()[0]
        conn.commit()
        session['usuario_id'] = novo_id
        session['nome'] = nome
        session['tipo'] = 'cliente'
        flash('Conta criada! Pode finalizar seu pedido.', 'success')
        return redirect(url_for('carrinho'))
    except:
        flash('E-mail ou CPF já cadastrado.', 'error')
    finally:
        cur.close(); conn.close()
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
        cur.execute('''INSERT INTO usuarios (nome, cpf, email, whatsapp, senha, tipo, aprovado) VALUES (%s, %s, %s, %s, %s, 'vendedor', FALSE);''', (nome, cpf, email, whatsapp, senha))
        conn.commit()
        flash('Solicitação enviada! Aguarde análise.', 'success')
    except:
        flash('E-mail ou CPF já cadastrado.', 'error')
    finally:
        cur.close(); conn.close()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada.', 'success')
    return redirect(url_for('index'))

@app.route('/meus-pedidos')
@login_required
def meus_pedidos():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('''
        SELECT id, valor_total, status_pagamento, mp_preference_id, TO_CHAR(data_pedido, 'DD/MM/YYYY HH24:MI') as data_formatada 
        FROM pedidos WHERE cliente_id = %s ORDER BY id DESC;
    ''', (session['usuario_id'],))
    pedidos_raw = cur.fetchall()
    
    pedidos = []
    for p in pedidos_raw:
        cur.execute('''
            SELECT ip.quantidade, COALESCE(pr.nome, 'Produto Excluído') as nome, COALESCE(pr.volume_ml, 0) as volume_ml
            FROM itens_pedido ip
            LEFT JOIN produtos pr ON ip.produto_id = pr.id
            WHERE ip.pedido_id = %s
        ''', (p['id'],))
        p['itens'] = cur.fetchall()
        pedidos.append(p)
        
    cur.close(); conn.close()
    return render_template('pedidos_cliente.html', pedidos=pedidos)

@app.route('/vendedor/painel')
@login_required
def vendedor_painel():
    if session.get('tipo') != 'vendedor': return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT SUM(valor_total) FROM pedidos WHERE vendedor_id = %s AND status_pagamento = 'aprovado'", (session['usuario_id'],))
    total_vendas = cur.fetchone()['sum'] or 0.0
    
    cur.execute("SELECT SUM(comissao_total) FROM pedidos WHERE vendedor_id = %s AND status_pagamento = 'aprovado' AND status_comissao = 'pendente'", (session['usuario_id'],))
    comissao_pendente = cur.fetchone()['sum'] or 0.0
    
    cur.execute("SELECT SUM(comissao_total) FROM pedidos WHERE vendedor_id = %s AND status_pagamento = 'aprovado' AND status_comissao = 'paga'", (session['usuario_id'],))
    comissao_paga = cur.fetchone()['sum'] or 0.0
    
    cur.execute('''
        SELECT p.id, p.valor_total, p.comissao_total, p.status_comissao, TO_CHAR(p.data_pedido, 'DD/MM/YYYY') as data_formatada, u.nome as cliente_nome
        FROM pedidos p JOIN usuarios u ON p.cliente_id = u.id
        WHERE p.vendedor_id = %s AND p.status_pagamento = 'aprovado' ORDER BY p.id DESC;
    ''', (session['usuario_id'],))
    vendas_raw = cur.fetchall()
    
    vendas = []
    for v in vendas_raw:
        cur.execute('''
            SELECT ip.quantidade, COALESCE(pr.nome, 'Produto Excluído') as nome, COALESCE(pr.volume_ml, 0) as volume_ml
            FROM itens_pedido ip
            LEFT JOIN produtos pr ON ip.produto_id = pr.id
            WHERE ip.pedido_id = %s
        ''', (v['id'],))
        v['itens'] = cur.fetchall()
        vendas.append(v)
        
    cur.close(); conn.close()
    
    host_url = request.url_root.rstrip('/')
    return render_template('vendedor_painel.html', total_vendas=total_vendas, comissao_pendente=comissao_pendente, comissao_paga=comissao_paga, vendas=vendas, host_url=host_url)

# ==========================================
# 6. MÓDULO GERENCIAL E CONFIGURAÇÕES (ADMIN)
# ==========================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(valor_total) FROM pedidos WHERE status_pagamento = 'aprovado';")
    faturamento = cur.fetchone()[0] or 0.0
    cur.execute('SELECT COUNT(*) FROM produtos;')
    total_produtos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM pedidos WHERE status_pagamento = 'aprovado';")
    total_pedidos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='vendedor' AND aprovado=FALSE;")
    pendentes = cur.fetchone()[0]
    cur.close(); conn.close()
    return render_template('admin.html', faturamento=faturamento, total_produtos=total_produtos, total_pedidos=total_pedidos, pendentes=pendentes)

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, nome, email, whatsapp, tipo, aprovado FROM usuarios ORDER BY id DESC;")
    usuarios = cur.fetchall()
    cur.close(); conn.close()
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuario/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_editar_usuario(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute('''UPDATE usuarios SET nome=%s, email=%s, whatsapp=%s, cpf=%s, tipo=%s, aprovado=%s WHERE id=%s''', 
                   (request.form['nome'], request.form['email'], request.form.get('whatsapp'), request.form.get('cpf'), request.form['tipo'], request.form['aprovado'] == '1', id))
        conn.commit(); cur.close(); conn.close()
        flash('Usuário atualizado com sucesso.', 'success')
        return redirect(url_for('admin_usuarios'))
    cur.execute('SELECT * FROM usuarios WHERE id = %s', (id,))
    u = cur.fetchone()
    cur.close(); conn.close()
    return render_template('admin_editar_usuario.html', u=u)

@app.route('/admin/usuario/excluir/<int:id>')
@admin_required
def admin_excluir_usuario(id):
    if id == session.get('usuario_id'): return redirect(url_for('admin_usuarios'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit(); cur.close(); conn.close()
    flash('Usuário removido da base de dados.', 'success')
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/configuracoes', methods=['GET', 'POST'])
@admin_required
def admin_config():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("UPDATE configuracoes SET valor = %s WHERE chave = 'mp_access_token'", (request.form['mp_access_token'].strip(),))
        conn.commit()
        flash('Token do Mercado Pago salvo com sucesso!', 'success')
        return redirect(url_for('admin_config'))
    cur.execute("SELECT valor FROM configuracoes WHERE chave = 'mp_access_token'")
    token = cur.fetchone()
    mp_token = token['valor'] if token else ''
    cur.close(); conn.close()
    return render_template('admin_config.html', mp_token=mp_token)

@app.route('/admin/comissao')
@admin_required
def admin_comissoes_gerais():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('''
        SELECT p.id, p.valor_total, p.comissao_total, p.status_comissao, p.status_pagamento, TO_CHAR(p.data_pedido, 'DD/MM/YYYY') as data_formatada, 
               u1.nome as cliente_nome, u2.nome as vendedor_nome
        FROM pedidos p 
        LEFT JOIN usuarios u1 ON p.cliente_id = u1.id
        LEFT JOIN usuarios u2 ON p.vendedor_id = u2.id
        ORDER BY p.id DESC;
    ''')
    vendas_raw = cur.fetchall()
    
    vendas = []
    for v in vendas_raw:
        cur.execute('''
            SELECT ip.quantidade, COALESCE(pr.nome, 'Produto Excluído') as nome, COALESCE(pr.volume_ml, 0) as volume_ml
            FROM itens_pedido ip
            LEFT JOIN produtos pr ON ip.produto_id = pr.id
            WHERE ip.pedido_id = %s
        ''', (v['id'],))
        v['itens'] = cur.fetchall()
        vendas.append(v)
        
    cur.close(); conn.close()
    return render_template('admin_comissao.html', vendas=vendas)

@app.route('/admin/comissao/pagar/<int:id>', methods=['POST'])
@admin_required
def pagar_comissao(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE pedidos SET status_comissao = 'paga' WHERE id = %s", (id,))
    conn.commit(); cur.close(); conn.close()
    flash('Comissão marcada como PAGA e repassada ao vendedor.', 'success')
    return redirect(url_for('admin_comissoes_gerais'))

@app.route('/admin/aprovacoes')
@admin_required
def admin_aprovacoes():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM usuarios WHERE tipo='vendedor' AND aprovado=FALSE ORDER BY id DESC;")
    r = cur.fetchall()
    cur.close(); conn.close()
    return render_template('admin_aprovacoes.html', revendedores=r)

@app.route('/admin/aprovar/<int:id>', methods=['POST'])
@admin_required
def aprovar_revendedor(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios SET aprovado = TRUE WHERE id = %s;", (id,))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('admin_aprovacoes'))

@app.route('/admin/estoque', methods=['GET', 'POST'])
@admin_required
def admin_estoque():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'novo_produto':
            n, v, p, c, e, d = request.form['nome'], request.form['volume_ml'], request.form['preco'], request.form['custo'], int(request.form['estoque']), request.form.get('descricao', '')
            img = request.files.get('imagem')
            img_b64 = base64.b64encode(img.read()).decode('utf-8') if img and img.filename != '' else None
            cur.execute('''INSERT INTO produtos (nome, descricao, preco, custo, volume_ml, estoque, imagem_base64) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;''', (n, d, p, c, v, e, img_b64))
            novo_id = cur.fetchone()['id']
            if e > 0: cur.execute('''INSERT INTO entradas_estoque (produto_id, quantidade, custo_unitario, data_compra) VALUES (%s, %s, %s, CURRENT_DATE);''', (novo_id, e, c))
        elif action == 'nova_entrada':
            pid, qtd, c, d = request.form['produto_id'], int(request.form['quantidade']), request.form['custo'], request.form['data_compra']
            cur.execute('''INSERT INTO entradas_estoque (produto_id, quantidade, custo_unitario, data_compra) VALUES (%s, %s, %s, %s);''', (pid, qtd, c, d))
            cur.execute('UPDATE produtos SET estoque = estoque + %s, custo = %s WHERE id = %s;', (qtd, c, pid))
        conn.commit()
        return redirect(url_for('admin_estoque'))
    data_hoje = datetime.today().strftime('%Y-%m-%d')
    cur.execute('SELECT * FROM produtos ORDER BY id DESC;')
    p = cur.fetchall()
    cur.execute('''SELECT e.quantidade, e.custo_unitario, TO_CHAR(e.data_compra, 'DD/MM/YYYY') as data_formatada, p.nome FROM entradas_estoque e JOIN produtos p ON e.produto_id = p.id ORDER BY e.data_compra DESC, e.id DESC;''')
    e = cur.fetchall()
    cur.close(); conn.close()
    return render_template('estoque.html', produtos=p, entradas=e, data_hoje=data_hoje)

@app.route('/admin/produto/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_editar_produto(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        n, v, p, c, d = request.form['nome'], request.form['volume_ml'], request.form['preco'], request.form['custo'], request.form.get('descricao', '')
        img = request.files.get('imagem')
        if img and img.filename != '':
            img_b64 = base64.b64encode(img.read()).decode('utf-8')
            cur.execute('''UPDATE produtos SET nome=%s, volume_ml=%s, preco=%s, custo=%s, descricao=%s, imagem_base64=%s WHERE id=%s''', (n, v, p, c, d, img_b64, id))
        else:
            cur.execute('''UPDATE produtos SET nome=%s, volume_ml=%s, preco=%s, custo=%s, descricao=%s WHERE id=%s''', (n, v, p, c, d, id))
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('admin_estoque'))
    cur.execute('SELECT * FROM produtos WHERE id = %s', (id,))
    p = cur.fetchone()
    cur.close(); conn.close()
    return render_template('editar_produto.html', p=p)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
