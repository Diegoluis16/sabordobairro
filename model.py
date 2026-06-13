import os
import psycopg2
import psycopg2.extras

# Puxa a URL do banco do Render automaticamente pelas variáveis de ambiente do servidor
DATABASE_URL = os.environ.get('DATABASE_URL')

def conectar_bd():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = conectar_bd()
    cursor = conn.cursor()
    
    # 1. Tabela de Cardápio/Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE,
            preco REAL NOT NULL
        )
    ''')
    
    # 2. Tabela de Comandas / Mesas / Delivery
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comandas (
            id SERIAL PRIMARY KEY,
            numero_mesa TEXT NOT NULL UNIQUE,
            itens_json TEXT NOT NULL,
            total REAL NOT NULL DEFAULT 0.0,
            observacoes TEXT DEFAULT ''
        )
    ''')
    
    # 3. Tabela de Usuários do Sistema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            nome_completo TEXT NOT NULL
        )
    ''')
    conn.commit()

    # Garante a inserção dos produtos iniciais se estiver zerado
    cursor.execute('SELECT COUNT(*) FROM produtos')
    if cursor.fetchone()[0] == 0:
        produtos_iniciais = [
            ("X-Burger", 18.50), ("X-Salada", 20.00),
            ("Batata Frita", 12.00), ("Refrigerante Lata", 6.00),
            ("Suco Natural", 8.50)
        ]
        for nome, preco in produtos_iniciais:
            cursor.execute('INSERT INTO produtos (nome, preco) VALUES (%s, %s) ON CONFLICT DO NOTHING', (nome, preco))
    
    # Garante a inserção do Administrador padrão se estiver zerado
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO usuarios (usuario, senha, nome_completo) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING', ('admin', 'admin', 'Administrador Principal'))
        
    conn.commit()
    cursor.close()
    conn.close()

# --- FUNÇÕES DE USUÁRIOS ---

def verificar_credenciais(usuario, senha):
    conn = conectar_bd()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT id, usuario, nome_completo FROM usuarios WHERE usuario = %s AND senha = %s', (usuario, senha))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(user) if user else None

def obter_todos_usuarios():
    conn = conectar_bd()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT id, usuario, nome_completo FROM usuarios')
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in linhas]

def salvar_novo_usuario(usuario, senha, nome_completo):
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO usuarios (usuario, senha, nome_completo) VALUES (%s, %s, %s)', (usuario, senha, nome_completo))
        conn.commit()
        sucesso = True
    except psycopg2.IntegrityError:
        sucesso = False
    cursor.close()
    conn.close()
    return sucesso

def alterar_usuario_bd(id_usuario, usuario, senha, nome_completo):
    conn = conectar_bd()
    cursor = conn.cursor()
    if senha.strip() == "":
        cursor.execute('UPDATE usuarios SET usuario = %s, nome_completo = %s WHERE id = %s', (usuario, nome_completo, id_usuario))
    else:
        cursor.execute('UPDATE usuarios SET usuario = %s, senha = %s, nome_completo = %s WHERE id = %s', (usuario, senha, nome_completo, id_usuario))
    conn.commit()
    cursor.close()
    conn.close()

def excluir_usuario_id(id_usuario):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id = %s', (id_usuario,))
    conn.commit()
    cursor.close()
    conn.close()

# --- FUNÇÕES DE PRODUTOS ---

def obter_todos_produtos():
    conn = conectar_bd()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT id, nome, preco FROM produtos')
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in linhas]

def salvar_novo_produto(nome, preco):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome, preco) VALUES (%s, %s) ON CONFLICT (nome) DO UPDATE SET preco = EXCLUDED.preco', (nome, float(preco)))
    conn.commit()
    cursor.close()
    conn.close()

def excluir_produto_id(id_produto):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM produtos WHERE id = %s', (id_produto,))
    conn.commit()
    cursor.close()
    conn.close()

# --- FUNÇÕES DE COMANDAS ---

def obter_todas_comandas():
    conn = conectar_bd()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT numero_mesa, itens_json, total, observacoes FROM comandas')
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in linhas]

def salvar_ou_atualizar_comanda(mesa, itens, total, obs):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO comandas (numero_mesa, itens_json, total, observacoes)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT(numero_mesa) DO UPDATE SET itens_json=EXCLUDED.itens_json, total=EXCLUDED.total, observacoes=EXCLUDED.observacoes
    ''', (mesa, itens, float(total), obs))
    conn.commit()
    cursor.close()
    conn.close()

def deletar_comanda_paga(mesa):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM comandas WHERE numero_mesa = %s', (mesa,))
    conn.commit()
    cursor.close()
    conn.close()






