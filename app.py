import time
from flask import Flask, jsonify, render_template, request, redirect, session
import model

# Inicializa o Flask mapeando a pasta 'modelos' trazida pelo Windows
app = Flask(__name__, template_folder='modelos')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# --- SEU MÉTODO DE LOGIN COM SEU GET TRADICIONAL RESTAURADO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('txt_usuario', '').strip()
        senha = request.form.get('txt_senha', '').strip()

        if not usuario or not senha:
            return render_template('login.html', erro="Usuário e senha são obrigatórios.")

        usuario_logado = model.verificar_credenciais(usuario, senha)

        if usuario_logado:
            session['user_id'] = usuario_logado['id']
            session['user_login'] = usuario_logado['usuario']
            session['user_nome'] = usuario_logado['nome_completo']
            return redirect('/')
        else:
            return render_template('login.html', erro="Usuário ou senha inválidos.")

    # O SEU GET PURO: Apenas mostra o formulário físico da pasta modelos sem travas
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('index.html', versao=str(time.time()), usuario_nome=session['user_nome'])

@app.route('/pedido')
def pedido_cliente():
    lista_produtos = model.obter_todos_produtos()
    return render_template('cliente.html', produtos_cardapio=lista_produtos)

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
