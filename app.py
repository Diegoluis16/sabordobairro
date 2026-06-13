import os
import time
from flask import Flask, jsonify, render_template, request, redirect, session
import model

# Inicializa o Flask mapeando a pasta 'modelos' trazida pelo Windows
app = Flask(__name__, template_folder='modelos')

# Chave de segurança estável aceita pelo Gunicorn do Render
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# --- CONFIGURAÇÃO ANTI-CACHE ---
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# GATILHO SEGURO DE INICIALIZAÇÃO NA INTERNET
@app.before_request
def inicializar_banco_na_nuvem():
    if not hasattr(app, 'banco_inicializado'):
        model.init_db()
        app.banco_inicializado = True

# NOVA ESTRUTURA BLINDADA: Injeta a tela de login como texto direto para evitar o erro de leitura do template
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('txt_usuario', '').strip()
        senha = request.form.get('txt_senha', '').strip()

        if not usuario or not senha:
            return "<h3>Usuário e senha são obrigatórios! <a href='/login'>Tentar novamente</a></h3>", 400

        # Tenta validar pelo banco de dados primeiro
        try:
            model.init_db()
            usuario_logado = model.verificar_credenciais(usuario, senha)
        except Exception:
            usuario_logado = None

        # ACESSO BLINDADO: Se for o admin padrão, libera o acesso mesmo se o banco do Linux travar a gravação
        if usuario_logado or (usuario == 'admin' and senha == 'admin'):
            session['user_id'] = 1
            session['user_login'] = 'admin'
            session['user_nome'] = 'Administrador Principal'
            return redirect('/')
        else:
            return "<h3>Usuário ou senha incorretos! <a href='/login'>Tentar novamente</a></h3>", 401


    # MÉTODO GET SEGURO: Entrega o formulário sem precisar ler a pasta do servidor
    html_login = '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sabor do Bairro - Login de Segurança</title>
        <style>
            :root { --primary: #cc0000; --dark: #2c3e50; }
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
            body { background: var(--dark); display: flex; justify-content: center; align-items: center; height: 100vh; }
            .login-card { background: white; padding: 30px; border-radius: 8px; width: 100%; max-width: 360px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
            .login-card h2 { text-align: center; color: var(--dark); margin-bottom: 20px; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #555; }
            .form-group input { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 15px; }
            .btn-entrar { background: var(--primary); color: white; border: none; width: 100%; padding: 12px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>Sabor do Bairro</h2>
            <form action="/login" method="POST">
                <div class="form-group">
                    <label>Usuário:</label>
                    <input type="text" name="txt_usuario" required placeholder="Ex: admin">
                </div>
                <div class="form-group">
                    <label>Senha:</label>
                    <input type="password" name="txt_senha" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn-entrar">ENTRAR NO SISTEMA</button>
            </form>
        </div>
    </body>
    </html>
    '''
    return html_login


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# --- ROTA PRINCIPAL DO CAIXA ---
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('index.html', versao=str(time.time()), usuario_nome=session['user_nome'])

# --- ROTA DO APP DO CLIENTE ---
@app.route('/pedido')
def pedido_cliente():
    lista_produtos = model.obter_todos_produtos()
    return render_template('cliente.html', produtos_cardapio=lista_produtos)

# --- ROTAS DA API: PRODUTOS ---
@app.route('/api/produtos', methods=['GET'])
def api_listar_produtos():
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autorizado'}), 401
    return jsonify(model.obter_todos_produtos())

@app.route('/api/produtos', methods=['POST'])
def api_cadastrar_produto():
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autorizado'}), 401
    dados = request.json
    nome = dados.get('nome', '').strip()
    preco = dados.get('preco')
    if not nome or preco is None:
        return jsonify({'erro': 'Dados inválidos'}), 400
    model.salvar_novo_produto(nome, preco)
    return jsonify({'sucesso': True})

@app.route('/api/produtos/<int:id_produto>', methods=['DELETE'])
def api_deletar_produto(id_produto):
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autorizado'}), 401
    model.excluir_produto_id(id_produto)
    return jsonify({'sucesso': True})

# --- ROTAS DA API: COMANDAS ---
@app.route('/api/comandas', methods=['GET'])
def api_listar_comandas():
    return jsonify(model.obter_todas_comandas())

@app.route('/api/comandas', methods=['POST'])
def api_salvar_comanda():
    dados = request.json
    mesa = dados.get('numero_mesa', '').strip()
    itens = dados.get('itens_json', '{}')
    total = dados.get('total', 0.0)
    obs = dados.get('observacoes', '')
    if not mesa:
        return jsonify({'erro': 'Mesa não informada'}), 400
    model.salvar_ou_atualizar_comanda(mesa, itens, total, obs)
    return jsonify({'sucesso': True})

@app.route('/api/comandas/<string:mesa>', methods=['DELETE'])
def api_fechar_comanda(mesa):
    model.deletar_comanda_paga(mesa)
    return jsonify({'sucesso': True})

# --- ROTAS DA API: GESTÃO DE USUÁRIOS ---
@app.route('/api/usuarios', methods=['GET'])
def api_listar_usuarios():
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autorizado'}), 401
    return jsonify(model.obter_todos_usuarios())

@app.route('/api/usuarios', methods=['POST'])
def api_cadastrar_usuario():
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autorizado'}), 401
    dados = request.json
    usuario = dados.get('usuario', '').strip()
    senha = dados.get('senha', '').strip()
    nome = dados.get('nome_completo', '').strip()
    
    if not usuario or not senha or not nome:
        return jsonify({'erro': 'Preencha todos os campos'}), 400
        
    criou = model.salvar_novo_usuario(usuario, senha, nome)
    if criou:
        return jsonify({'sucesso': True})
    return jsonify({'erro': 'Este nome de usuário já existe'}), 400

@app.route('/api/usuarios/<int:id_usuario>', methods=['DELETE'])
def api_deletar_usuario(id_usuario):
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autorizado'}), 401
    model.excluir_usuario_id(id_usuario)
    return jsonify({'sucesso': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



