import sqlite3

# CONFIGURAÇÃO DE NUVEM: Utiliza a pasta temporária /tmp/ que possui permissão de gravação no Render
DATABASE = '/tmp/sabor_bairro_mvc.db'

def conectar_bd():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = conectar_bd()
    cursor = conn.cursor()
    
    # 1. Tabela de Cardápio/Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            preco REAL NOT NULL
        )
    ''')
    
    # 2. Tabela de Comandas / Mesas / Delivery
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comandas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_mesa TEXT NOT NULL UNIQUE,
            itens_json TEXT NOT NULL,
            total REAL NOT NULL DEFAULT 0.0,
            observacoes TEXT DEFAULT ''
        )
    ''')
    
    # 3. Tabela de Usuários do Sistema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        cursor.executemany('INSERT INTO produtos (nome, preco) VALUES (?, ?)', produtos_iniciais)
    
    # Garante a inserção do Administrador padrão se estiver zerado
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO usuarios (usuario, senha, nome_completo) VALUES (?, ?, ?)', ('admin', 'admin', 'Administrador Principal'))
        
    conn.commit()
    conn.close()

init_db()

# --- FUNÇÕES DE USUÁRIOS ---

def verificar_credenciais(usuario, senha):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT id, usuario, nome_completo FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, senha))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def obter_todos_usuarios():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT id, usuario, nome_completo FROM usuarios')
    linhas = cursor.fetchall()
    conn.close()
    return [dict(r) for r in linhas]

def salvar_novo_usuario(usuario, senha, nome_completo):
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO usuarios (usuario, senha, nome_completo) VALUES (?, ?, ?)', (usuario, senha, nome_completo))
        conn.commit()
        sucesso = True
    except sqlite3.IntegrityError:
        sucesso = False
    conn.close()
    return sucesso

def alterar_usuario_bd(id_usuario, usuario, senha, nome_completo):
    conn = conectar_bd()
    cursor = conn.cursor()
    if senha.strip() == "":
        cursor.execute('UPDATE usuarios SET usuario = ?, nome_completo = ? WHERE id = ?', (usuario, nome_completo, id_usuario))
    else:
        cursor.execute('UPDATE usuarios SET usuario = ?, senha = ?, nome_completo = ? WHERE id = ?', (usuario, senha, nome_completo, id_usuario))
    conn.commit()
    conn.close()

def excluir_usuario_id(id_usuario):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id = ?', (id_usuario,))
    conn.commit()
    conn.close()

# --- FUNÇÕES DE PRODUTOS ---

def obter_todos_produtos():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, preco FROM produtos')
    linhas = cursor.fetchall()
    conn.close()
    return [dict(r) for r in linhas]

def salvar_novo_produto(nome, preco):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO produtos (nome, preco) VALUES (?, ?)', (nome, float(preco)))
    conn.commit()
    conn.close()

def excluir_produto_id(id_produto):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM produtos WHERE id = ?', (id_produto,))
    conn.commit()
    conn.close()

# --- FUNÇÕES DE COMANDAS ---

def obter_todas_comandas():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT numero_mesa, itens_json, total, observacoes FROM comandas')
    linhas = cursor.fetchall()
    conn.close()
    return [dict(r) for r in linhas]

def salvar_ou_atualizar_comanda(mesa, itens, total, obs):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO comandas (numero_mesa, itens_json, total, observacoes)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(numero_mesa) DO UPDATE SET itens_json=excluded.itens_json, total=excluded.total, observacoes=excluded.observacoes
    ''', (mesa, itens, float(total), obs))
    conn.commit()
    conn.close()

def deletar_comanda_paga(mesa):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM comandas WHERE numero_mesa = ?', (mesa,))
    conn.commit()
    conn.close()





