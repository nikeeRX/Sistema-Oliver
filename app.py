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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OLIVA - Fragrância em Decants</title>
        <style>
            body, h1, h2, h3, p, ul, form { margin: 0; padding: 0; box-sizing: border-box; }
            body { background-color: #fcfaf7; color: #332d27; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 300; }
            .navbar { background-color: transparent; padding: 30px 0; border-bottom: 1px solid #eae1d3; }
            .nav-container { max-width: 1100px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
            .logo-text { font-family: 'Times New Roman', Georgia, serif; font-size: 26pt; font-weight: normal; color: #b89758; text-decoration: none; letter-spacing: 8px; text-transform: uppercase; }
            .navbar nav a { color: #665b4f; text-decoration: none; margin-left: 25px; font-size: 10pt; letter-spacing: 1px; text-transform: uppercase; transition: color 0.3s; }
            .navbar nav a:hover { color: #b89758; }
            .content-container { max-width: 1100px; margin: 50px auto; padding: 0 20px; min-height: 60vh; }
            .hero-section { text-align: center; margin-bottom: 60px; padding: 20px 0; }
            .hero-section h2 { font-family: 'Times New Roman', Georgia, serif; font-size: 24pt; font-weight: normal; margin-bottom: 15px; color: #2c2621; letter-spacing: 2px; }
            .hero-section p { color: #8c764d; font-style: italic; font-size: 11pt; letter-spacing: 1px; }
            .page-title { font-family: 'Times New Roman', Georgia, serif; font-weight: normal; font-size: 22pt; margin-bottom: 30px; color: #2c2621; letter-spacing: 1px; text-align: center; }
            
            /* Grid de Produtos */
            .products-grid { display: flex; flex-wrap: wrap; gap: 2%; }
            .product-card { background: #ffffff; border: 1px solid #f2ecdf; width: 31%; margin-bottom: 40px; border-radius: 6px; overflow: hidden; transition: all 0.4s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.02); }
            .product-card:hover { transform: translateY(-5px); box-shadow: 0 12px 25px rgba(184, 151, 88, 0.1); border-color: #dfd5c6; }
            .product-img-placeholder { background: linear-gradient(135deg, #fffcf7 0%, #f4ede1 100%); height: 260px; display: flex; flex-direction: column; align-items: center; justify-content: center; border-bottom: 1px solid #f2ecdf; }
            .img-icon { font-size: 28pt; color: #b89758; margin-bottom: 10px; opacity: 0.8; }
            .product-img-placeholder span.marca { color: #8c764d; font-family: 'Times New Roman', Georgia, serif; font-size: 11pt; letter-spacing: 4px; text-transform: uppercase; opacity: 0.7; }
            .product-img-real { height: 260px; width: 100%; border-bottom: 1px solid #f2ecdf; background-color: #fff; display: flex; align-items: center; justify-content: center; overflow: hidden; }
            .product-img-real img { width: 100%; height: 100%; object-fit: cover; }
            
            .product-info { padding: 25px 20px; text-align: center; }
            .product-info h3 { font-size: 14pt; margin-bottom: 8px; color: #2c2621; font-weight: 500; letter-spacing: 1px; }
            .volumetria { font-size: 9pt; color: #b89758; font-weight: bold; margin-bottom: 12px; letter-spacing: 1px; }
            .description { font-size: 9.5pt; color: #7a7065; margin-bottom: 20px; height: 42px; overflow: hidden; line-height: 1.5; }
            .price { font-size: 15pt; color: #2c2621; margin-bottom: 20px; font-family: 'Times New Roman', Georgia, serif; }
            
            /* Dashboard e Forms */
            .dashboard-cards { display: flex; gap: 20px; margin-bottom: 40px; }
            .card { background: #ffffff; padding: 30px; border: 1px solid #eae1d3; border-top: 3px solid #b89758; flex: 1; border-radius: 6px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.02); }
            .card h3 { color: #8c764d; font-size: 9pt; margin-bottom: 15px; letter-spacing: 2px; }
            .card p { font-size: 28pt; color: #2c2621; font-family: 'Times New Roman', Georgia, serif; }
            .form-group { margin-bottom: 20px; text-align: left; }
            label { display: block; font-weight: 500; margin-bottom: 8px; font-size: 9pt; color: #665b4f; text-transform: uppercase; letter-spacing: 1px; }
            input, textarea, select { width: 100%; padding: 12px; border: 1px solid #dfd5c6; border-radius: 4px; font-family: inherit; background-color: #fffcf7; transition: border 0.3s; }
            input:focus, textarea:focus, select:focus { outline: none; border-color: #b89758; }
            input[type="file"] { background-color: #fff; padding: 9px; }
            
            /* Botões e Alertas */
            .btn-primary { background-color: #b89758; color: #ffffff; border: none; width: 100%; padding: 14px; font-size: 9pt; text-transform: uppercase; letter-spacing: 2px; font-weight: 500; cursor: pointer; border-radius: 4px; transition: all 0.3s; }
            .btn-primary:hover { background-color: #2c2621; color: #b89758; }
            .btn-secondary { background-color: transparent; color: #665b4f; border: 1px solid #dfd5c6; padding: 14px 20px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; text-transform: uppercase; font-size: 9pt; letter-spacing: 1px; transition: all 0.3s; }
            .btn-secondary:hover { background-color: #f2ecdf; }
            .alert { padding: 15px; margin-bottom: 25px; border-radius: 4px; background-color: #fdfbf7; border-left: 4px solid #b89758; color: #665b4f; font-size: 10pt; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
            
            /* Tabelas */
            table { width: 100%; border-collapse: collapse; margin-bottom: 30px; background: #fff; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
            th, td { padding: 18px 15px; text-align: left; border-bottom: 1px solid #f2ecdf; }
            th { background-color: #fffcf7; color: #8c764d; font-size: 9pt; text-transform: uppercase; letter-spacing: 1px; font-weight: 500; }
            tr:hover { background-color: #fdfbf7; }
            
            /* Rodape */
            .main-footer { text-align: center; padding: 50px 0; margin-top: 60px; font-size: 9pt; color: #a39686; border-top: 1px solid #eae1d3; letter-spacing: 1px; }
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
                        <a href="/logout" style="color: #a39686;">Sair</a>
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
            <p>OLIVA &copy; 2026. A ARTE DA FRAGRÂNCIA EM DECANTS.</p>
        </footer>
    </body>
    </html>
    ''',
    
    'index.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <div class="hero-section">
        <h2>A Essência da Exclusividade</h2>
        <p>A sofisticação das maiores grifes do mundo, na volumetria perfeita para você.</p>
    </div>
    <div class="products-grid">
        {% for produto in produtos %}
        <div class="product-card">
            
            <!-- Imagem puxando direto do Banco de Dados via Base64 -->
            {% if produto.imagem_base64 %}
                <div class="product-img-real">
                    <img src="data:image/jpeg;base64,{{ produto.imagem_base64 }}" alt="{{ produto.nome }}">
                </div>
            {% else %}
                <div class="product-img-placeholder">
                    <div class="img-icon">✧</div>
                    <span class="marca">OLIVA</span>
                </div>
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
        <p style="text-align: center; width: 100%; color: #8c764d; font-style: italic;">Nosso catálogo está sendo atualizado com novas essências.</p>
        {% endfor %}
    </div>
    {% endblock %}
    ''',
    
    'carrinho.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Carrinho de Compras</h2>
    {% if produtos %}
        <table>
            <tr><th>Fragrância</th><th>Volumetria</th><th>Quantidade</th><th>Subtotal</th></tr>
            {% for p in produtos %}
            <tr>
                <td style="color: #2c2621; font-weight: 500;">{{ p.nome }}</td>
                <td style="color: #8c764d;">{{ p.volume_ml }}ml</td>
                <td>{{ p.quantidade }}</td>
                <td style="font-family: 'Times New Roman', serif; font-size: 12pt;">R$ {{ "%.2f"|format(p.subtotal) }}</td>
            </tr>
            {% endfor %}
        </table>
        <h3 style="text-align: right; margin-bottom: 30px; color: #2c2621; font-family: 'Times New Roman', serif; font-size: 18pt;">Total: R$ {{ "%.2f"|format(total) }}</h3>
        <div style="text-align: right;">
            <a href="/carrinho/limpar" style="color: #a39686; margin-right: 30px; text-decoration: none; font-size: 9pt; text-transform: uppercase; letter-spacing: 1px;">Esvaziar Carrinho</a>
            <button class="btn-primary" style="width: 250px;" onclick="alert('Pagamento em breve!')">Finalizar Pedido</button>
        </div>
    {% else %}
        <div style="text-align: center; padding: 80px 0;">
            <p style="font-size: 12pt; color: #a39686; margin-bottom: 30px; font-style: italic;">Sua seleção está vazia.</p>
            <a href="/" class="btn-primary" style="text-decoration: none; padding: 12px 30px; display: inline-block; width: auto;">Descobrir Fragrâncias</a>
        </div>
    {% endif %}
    {% endblock %}
    ''',

    'login.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <div style="max-width: 420px; margin: 40px auto 0; background: #fff; padding: 50px 40px; border: 1px solid #f2ecdf; border-radius: 6px; box-shadow: 0 10px 30px rgba(0,0,0,0.02);">
        <h2 style="text-align: center; margin-bottom: 40px; font-family: 'Times New Roman', serif; color: #2c2621; font-size: 20pt; letter-spacing: 1px;">Acesso Exclusivo</h2>
        <form method="POST" action="/login">
            <div class="form-group">
                <label>E-mail de Acesso</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group" style="margin-bottom: 40px;">
                <label>Senha</label>
                <input type="password" name="senha" required>
            </div>
            <button type="submit" class="btn-primary">Entrar</button>
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
            <h3>Pedidos Pendentes</h3>
            <p>0</p>
        </div>
    </div>
    {% endblock %}
    ''',
    
    'estoque.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Gestão e Histórico de Estoque</h2>
    
    <div style="display: flex; gap: 30px; margin-bottom: 50px; flex-wrap: wrap;">
        
        <!-- 1. CADASTRAR NOVO PRODUTO (Agora com Upload de Foto) -->
        <div style="background: #fff; padding: 35px; border: 1px solid #f2ecdf; border-radius: 6px; flex: 1; min-width: 400px;">
            <h3 style="margin-bottom: 25px; color: #2c2621; font-weight: normal; font-family: 'Times New Roman', serif; font-size: 16pt;">1. Cadastrar Nova Fragrância</h3>
            <form method="POST" action="/admin/estoque" enctype="multipart/form-data" style="display: flex; flex-wrap: wrap; gap: 15px;">
                <input type="hidden" name="action" value="novo_produto">
                
                <div class="form-group" style="width: 100%; margin-bottom: 0;">
                    <label>Nome do Perfume</label>
                    <input type="text" name="nome" required>
                </div>
                
                <div class="form-group" style="width: 47%; margin-bottom: 0;">
                    <label>Volumetria (ml)</label>
                    <input type="number" name="volume_ml" required>
                </div>
                <div class="form-group" style="width: 47%; margin-bottom: 0;">
                    <label>Estoque Inicial</label>
                    <input type="number" name="estoque" required value="0">
                </div>
                
                <div class="form-group" style="width: 47%; margin-bottom: 0;">
                    <label>Custo Pago (R$)</label>
                    <input type="number" step="0.01" name="custo" required placeholder="0.00">
                </div>
                <div class="form-group" style="width: 47%; margin-bottom: 0;">
                    <label>Preço Venda (R$)</label>
                    <input type="number" step="0.01" name="preco" required placeholder="0.00">
                </div>
                
                <div class="form-group" style="width: 100%; margin-bottom: 0;">
                    <label>Foto do Produto (Upload)</label>
                    <input type="file" name="imagem" accept="image/*">
                </div>

                <div class="form-group" style="width: 100%; margin-bottom: 15px;">
                    <label>Descrição Olfativa</label>
                    <textarea name="descricao" rows="2"></textarea>
                </div>
                <button type="submit" class="btn-primary">Criar Cadastro</button>
            </form>
        </div>

        <!-- 2. REPOSIÇÃO DE ESTOQUE (COMPRAS) -->
        <div style="background: #fff; padding: 35px; border: 1px solid #f2ecdf; border-radius: 6px; flex: 1; min-width: 400px;">
            <h3 style="margin-bottom: 25px; color: #2c2621; font-weight: normal; font-family: 'Times New Roman', serif; font-size: 16pt;">2. Registrar Compra (Reposição)</h3>
            <form method="POST" action="/admin/estoque" style="display: flex; flex-wrap: wrap; gap: 15px;">
                <input type="hidden" name="action" value="nova_entrada">
                
                <div class="form-group" style="width: 100%; margin-bottom: 0;">
                    <label>Selecione a Fragrância</label>
                    <select name="produto_id" required>
                        <option value="">-- Escolha o Decant --</option>
                        {% for p in produtos %}
                            <option value="{{ p.id }}">{{ p.nome }} ({{ p.volume_ml }}ml)</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group" style="width: 100%; margin-bottom: 0;">
                    <label>Data da Compra</label>
                    <input type="date" name="data_compra" required value="{{ data_hoje }}">
                </div>

                <div class="form-group" style="width: 47%; margin-bottom: 0;">
                    <label>Qtd Comprada</label>
                    <input type="number" name="quantidade" required min="1">
                </div>
                <div class="form-group" style="width: 47%; margin-bottom: 15px;">
                    <label>Custo Unitário Pago (R$)</label>
                    <input type="number" step="0.01" name="custo" required>
                </div>

                <button type="submit" class="btn-primary" style="background-color: #2c2621; color: #b89758; margin-top: auto;">Gravar Estoque</button>
            </form>
        </div>
    </div>

    <h3 style="margin-bottom: 20px; color: #2c2621; font-weight: normal; font-family: 'Times New Roman', serif; font-size: 16pt;">Catálogo Atual & Edição</h3>
    <table style="margin-bottom: 50px;">
        <tr><th>Ref</th><th>Foto</th><th>Fragrância</th><th>Custo</th><th>Venda</th><th>Estoque</th><th>Ação</th></tr>
        {% for p in produtos %}
        <tr>
            <td style="color: #a39686;">#{{ p.id }}</td>
            <td>
                {% if p.imagem_base64 %}
                    <img src="data:image/jpeg;base64,{{ p.imagem_base64 }}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #eae1d3;">
                {% else %}
                    <div style="width: 40px; height: 40px; background: #fcfaf7; border: 1px solid #eae1d3; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 8pt; color: #b89758;">✧</div>
                {% endif %}
            </td>
            <td style="color: #2c2621; font-weight: 500;">{{ p.nome }} <span style="color: #8c764d; font-size: 9pt;">({{ p.volume_ml }}ml)</span></td>
            <td style="color: #666; font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(p.custo) if p.custo else "0.00" }}</td>
            <td style="font-family: 'Times New Roman', serif; color: #2c2621; font-weight: bold;">R$ {{ "%.2f"|format(p.preco) }}</td>
            <td>
                <span style="padding: 6px 12px; background: {% if p.estoque < 5 %}#fffcf7{% else %}transparent{% endif %}; border: 1px solid {% if p.estoque < 5 %}#b89758{% else %}#eae1d3{% endif %}; border-radius: 4px; font-size: 9pt; color: #665b4f;">
                    {{ p.estoque }} un
                </span>
            </td>
            <td>
                <a href="/admin/produto/editar/{{ p.id }}" style="color: #b89758; text-decoration: none; font-size: 9pt; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">Editar</a>
            </td>
        </tr>
        {% endfor %}
    </table>

    <h3 style="margin-bottom: 20px; color: #2c2621; font-weight: normal; font-family: 'Times New Roman', serif; font-size: 16pt;">Histórico de Compras (Entradas)</h3>
    <table>
        <tr><th>Data</th><th>Fragrância</th><th>Qtd</th><th>Custo Un.</th><th>Total Pago</th></tr>
        {% for entrada in entradas %}
        <tr>
            <td style="color: #a39686;">{{ entrada.data_formatada }}</td>
            <td style="color: #2c2621; font-weight: 500;">{{ entrada.nome }}</td>
            <td><span style="padding: 4px 8px; background: #eefaf2; color: #3c763d; border-radius: 4px; font-weight: bold; font-size: 9pt;">+{{ entrada.quantidade }}</span></td>
            <td style="font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(entrada.custo_unitario) }}</td>
            <td style="font-family: 'Times New Roman', serif; color: #8c764d; font-weight: bold;">R$ {{ "%.2f"|format(entrada.quantidade * entrada.custo_unitario) }}</td>
        </tr>
        {% else %}
        <tr><td colspan="5" style="text-align: center; color: #a39686; font-style: italic;">Nenhuma compra registrada no histórico.</td></tr>
        {% endfor %}
    </table>
    {% endblock %}
    ''',
    
    'editar_produto.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Editar Fragrância: {{ p.nome }}</h2>
    
    <div style="background: #fff; padding: 40px; border: 1px solid #f2ecdf; border-radius: 6px; max-width: 800px; margin: 0 auto; margin-bottom: 50px;">
        <form method="POST" action="/admin/produto/editar/{{ p.id }}" enctype="multipart/form-data" style="display: flex; flex-wrap: wrap; gap: 20px;">
            
            <div class="form-group" style="width: 100%; margin-bottom: 0;">
                <label>Nome do Perfume</label>
                <input type="text" name="nome" required value="{{ p.nome }}">
            </div>
            
            <div class="form-group" style="width: 47%; margin-bottom: 0;">
                <label>Volumetria (ml)</label>
                <input type="number" name="volume_ml" required value="{{ p.volume_ml }}">
            </div>
            <div class="form-group" style="width: 47%; margin-bottom: 0;">
                <label>Custo Base Atual (R$)</label>
                <input type="number" step="0.01" name="custo" required value="{{ p.custo }}">
            </div>
            
            <div class="form-group" style="width: 47%; margin-bottom: 0;">
                <label>Preço Venda (R$)</label>
                <input type="number" step="0.01" name="preco" required value="{{ p.preco }}">
            </div>
            
            <div class="form-group" style="width: 100%; margin-bottom: 0;">
                <label>Atualizar Foto do Produto</label>
                <input type="file" name="imagem" accept="image/*">
                <p style="font-size: 8.5pt; color: #a39686; margin-top: 5px;">* Deixe em branco se não quiser alterar a foto atual.</p>
                {% if p.imagem_base64 %}
                    <div style="margin-top: 15px; border: 1px solid #eae1d3; padding: 5px; display: inline-block; border-radius: 4px; background: #fffcf7;">
                        <img src="data:image/jpeg;base64,{{ p.imagem_base64 }}" alt="Preview" style="height: 80px; border-radius: 2px;">
                    </div>
                {% endif %}
            </div>

            <div class="form-group" style="width: 100%; margin-bottom: 10px;">
                <label>Descrição Olfativa</label>
                <textarea name="descricao" rows="4">{{ p.descricao }}</textarea>
            </div>
            
            <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f2ecdf; padding-top: 25px; margin-top: 10px;">
                <a href="/admin/estoque" class="btn-secondary">Voltar sem Salvar</a>
                <button type="submit" class="btn-primary" style="width: auto; padding: 14px 50px;">Salvar Alterações</button>
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
        <span style="color: #2c2621; font-weight: bold;">Análise de Lucro:</span> A tabela detalha a margem bruta (Preço de Venda menos Custo Pago) e calcula a comissão padrão de <strong>10%</strong> sobre a venda final.
    </div>
    <table>
        <tr><th>Fragrância</th><th>Custo Pago</th><th>Preço Venda</th><th>Lucro Bruto</th><th>Comissão (10% Venda)</th></tr>
        {% for p in produtos %}
        <tr>
            <td style="color: #2c2621;">{{ p.nome }} <span style="color: #8c764d; font-size: 9pt;">({{ p.volume_ml }}ml)</span></td>
            <td style="color: #d9534f; font-family: 'Times New Roman', serif;">- R$ {{ "%.2f"|format(p.custo) if p.custo else "0.00" }}</td>
            <td style="color: #2c2621; font-family: 'Times New Roman', serif;">R$ {{ "%.2f"|format(p.preco) }}</td>
            <td style="color: #3c763d; font-family: 'Times New Roman', serif; font-weight: bold;">R$ {{ "%.2f"|format(p.preco - (p.custo or 0)) }}</td>
            <td style="color: #b89758; font-family: 'Times New Roman', serif; font-size: 12pt; font-weight: bold;">R$ {{ "%.2f"|format(p.preco * 0.10) }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endblock %}
    ''',

    'pedidos.html': '''
    {% extends 'base.html' %}
    {% block content %}
    <h2 class="page-title">Minha Coleção</h2>
    <div style="background: #fff; padding: 60px 20px; text-align: center; border: 1px solid #f2ecdf; border-radius: 6px;">
        <p style="color: #a39686; font-size: 11pt; margin-bottom: 30px; font-style: italic;">Sua jornada olfativa ainda não começou.</p>
        <a href="/" class="btn-primary" style="text-decoration: none; padding: 12px 30px; display: inline-block; width: auto;">Explorar o Catálogo</a>
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
    
    # Adiciona colunas para Custo e Imagem Base64 de forma segura
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='produtos' AND column_name='custo';")
    if not cur.fetchone():
        cur.execute("ALTER TABLE produtos ADD COLUMN custo NUMERIC(10,2) DEFAULT 0;")
        
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='produtos' AND column_name='imagem_base64';")
    if not cur.fetchone():
        cur.execute("ALTER TABLE produtos ADD COLUMN imagem_base64 TEXT;")
        
    cur.execute('''
        CREATE TABLE IF NOT EXISTS entradas_estoque (
            id SERIAL PRIMARY KEY,
            produto_id INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
            quantidade INTEGER NOT NULL,
            custo_unitario NUMERIC(10,2) NOT NULL,
            data_compra DATE DEFAULT CURRENT_DATE
        );
    ''')
    
    cur.execute('SELECT COUNT(*) FROM usuarios;')
    if cur.fetchone()[0] == 0:
        senha_hash = generate_password_hash('admin123')
        cur.execute('''
            INSERT INTO usuarios (nome, email, senha, is_admin)
            VALUES ('Admin Oliva', 'admin@oliva.com', %s, TRUE);
        ''', (senha_hash,))

    conn.commit()
    cur.close()
    conn.close()

try:
    init_db()
    print("Banco blindado para Produção! Fotos em Base64 ativadas.")
except Exception as e:
    print(f"Aguardando banco... {e}")


# ==========================================
# 3. ROTAS DE SEGURANÇA E PROTEÇÃO
# ==========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Área restrita. Por favor, identifique-se.', 'error')
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
# 4. ROTAS PÚBLICAS
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
            cur.execute('SELECT id, nome, preco, volume_ml FROM produtos WHERE id = %s;', (id_produto,))
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
            flash('Credenciais inválidas. Tente novamente.', 'error')
    return render_template('login.html')

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
# 5. ROTAS GERENCIAIS (ESTOQUE, UPLOAD E EDIÇÃO)
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
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'novo_produto':
            nome = request.form['nome']
            volume_ml = request.form['volume_ml']
            preco = request.form['preco']
            custo = request.form['custo']
            estoque_inicial = int(request.form['estoque'])
            descricao = request.form.get('descricao', '')
            
            # Tratamento da Imagem enviada
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
            
            cur.execute('''
                UPDATE produtos 
                SET estoque = estoque + %s, custo = %s 
                WHERE id = %s;
            ''', (quantidade, custo, produto_id))
            
            flash('Compra computada e estoque atualizado com sucesso!', 'success')

        conn.commit()
        return redirect(url_for('admin_estoque'))
    
    data_hoje = datetime.today().strftime('%Y-%m-%d')
    cur.execute('SELECT * FROM produtos ORDER BY id DESC;')
    produtos = cur.fetchall()
    
    cur.execute('''
        SELECT e.quantidade, e.custo_unitario, TO_CHAR(e.data_compra, 'DD/MM/YYYY') as data_formatada, p.nome 
        FROM entradas_estoque e
        JOIN produtos p ON e.produto_id = p.id
        ORDER BY e.data_compra DESC, e.id DESC;
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
        
        # Tratamento da Imagem enviada na Edição
        imagem_file = request.files.get('imagem')
        
        if imagem_file and imagem_file.filename != '':
            imagem_b64 = base64.b64encode(imagem_file.read()).decode('utf-8')
            cur.execute('''
                UPDATE produtos 
                SET nome=%s, volume_ml=%s, preco=%s, custo=%s, descricao=%s, imagem_base64=%s
                WHERE id=%s
            ''', (nome, volume_ml, preco, custo, descricao, imagem_b64, id))
        else:
            # Atualiza tudo, exceto a imagem (mantém a que já está lá)
            cur.execute('''
                UPDATE produtos 
                SET nome=%s, volume_ml=%s, preco=%s, custo=%s, descricao=%s
                WHERE id=%s
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
        flash('Produto não encontrado.', 'error')
        return redirect(url_for('admin_estoque'))
        
    return render_template('editar_produto.html', p=produto)

@app.route('/admin/comissao')
@admin_required
def admin_comissao():
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
