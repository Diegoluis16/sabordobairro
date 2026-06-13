import sqlite3

DATABASE = '/tmp/sabor_bairro_mvc.db'

def conectar_bd():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, preco REAL NOT NULL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS comandas (id INTEGER PRIMARY KEY AUTOINCREMENT, numero_mesa TEXT NOT NULL UNIQUE, itens_json TEXT NOT NULL, total REAL NOT NULL DEFAULT 0.0, observacoes TEXT DEFAULT \'\')')
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT NOT NULL UNIQUE, senha TEXT NOT NULL, nome_completo TEXT NOT NULL)')
    conn.commit()

    cursor.execute('SELECT COUNT(*) FROM produtos')
    if cursor.fetchone() == 0:
        produtos_iniciais = [("X-Burger", 18.50), ("X-Salada", 20.00), ("Batata Frita", 12.00), ("Refrigerante Lata", 6.00), ("Suco Natural", 8.50)]
        cursor.executemany('INSERT OR IGNORE INTO produtos (nome, preco) VALUES (?, ?)', produtos_iniciais)
    conn.commit()
    conn.close()

# --- FUNÇÃO DE VALIDAÇÃO FIXA NA MEMÓRIA ---
def verificar_credenciais(usuario, senha):
    # ACESSO MASTER DEFINITIVO: Não consulta o arquivo e aceita direto admin / admin
    if usuario == 'admin' and senha == 'admin':
        return {"id": 1, "usuario": "admin", "nome_completo": "Administrador Principal"}
    
    # Se for outro funcionário cadastrado, tenta ler o banco de dados temporário
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('SELECT id, usuario, nome_completo FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, senha))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception:
        return None

def obter_todos_usuarios():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('SELECT id, usuario, nome_completo FROM usuarios')
        linhas = cursor.fetchall()
        conn.close()
        lista = [dict(r) for r in linhas]
    except Exception:
        lista = []
    
    # Sempre garante o admin fixo aparecendo listado na tela de gerenciamento
    if not any(u['usuario'] == 'admin' for u in lista):
        lista.insert(0, {"id": 1, "usuario": "admin", "nome_completo": "Administrador Principal"})
    return lista

def salvar_novo_usuario(usuario, senha, nome_completo):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO usuarios (usuario, senha, nome_completo) VALUES (?, ?, ?)', (usuario, senha, nome_completo))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def excluir_usuario_id(id_usuario):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM usuarios WHERE id = ?', (id_usuario,))
        conn.commit()
        conn.close()
    except Exception:
        pass

def obter_todos_produtos():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, preco FROM produtos')
        linhas = cursor.fetchall()
        conn.close()
        return [dict(r) for r in linhas]
    except Exception:
        return []

def salvar_novo_produto(nome, preco):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO produtos (nome, preco) VALUES (?, ?)', (nome, float(preco)))
        conn.commit()
        conn.close()
    except Exception:
        pass

def excluir_produto_id(id_produto):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produtos WHERE id = ?', (id_produto,))
        conn.commit()
        conn.close()
    except Exception:
        pass

def obter_todas_comandas():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('SELECT numero_mesa, itens_json, total, observacoes FROM comandas')
        linhas = cursor.fetchall()
        conn.close()
        return [dict(r) for r in linhas]
    except Exception:
        return []

def salvar_ou_atualizar_comanda(mesa, itens, total, obs):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO comandas (numero_mesa, itens_json, total, observacoes) VALUES (?, ?, ?, ?) ON CONFLICT(numero_mesa) DO UPDATE SET itens_json=excluded.itens_json, total=excluded.total, observacoes=excluded.observacoes', (mesa, itens, float(total), obs))
        conn.commit()
        conn.close()
    except Exception:
        pass

def deletar_comanda_paga(mesa):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM comandas WHERE numero_mesa = ?', (mesa,))
        conn.commit()
        conn.close()
    except Exception:
        pass
