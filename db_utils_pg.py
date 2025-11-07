import psycopg2
import os
from datetime import datetime

# Configuração do banco (Render)
DB_URL = os.getenv("DATABASE_URL", "postgresql://halldb_user:dCu5hXO8okI8Qz0j9LK9i7AcZI3LYND0@dpg-d43e2ommcj7s73b062jg-a/halldb")

def get_conn():
    return psycopg2.connect(DB_URL)

# Inicializa todas as tabelas
def inicializar_banco():
    conn = get_conn()
    cur = conn.cursor()

    # Tabela de clientes
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        cpf VARCHAR(14) PRIMARY KEY,
        nome TEXT NOT NULL,
        telefone TEXT,
        endereco TEXT
    );
    """)

    # Tabela de produtos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        descricao TEXT NOT NULL,
        preco NUMERIC(10,2) NOT NULL,
        categoria TEXT
    );
    """)

    # Tabela de pedidos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id SERIAL PRIMARY KEY,
        cliente_cpf VARCHAR(14) REFERENCES clientes(cpf),
        data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total NUMERIC(10,2),
        status TEXT DEFAULT 'Pendente'
    );
    """)

    # Tabela de itens
    cur.execute("""
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id SERIAL PRIMARY KEY,
        pedido_id INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
        produto_id INTEGER REFERENCES produtos(id),
        quantidade INTEGER,
        subtotal NUMERIC(10,2)
    );
    """)

    # Verifica se já existem produtos
    cur.execute("SELECT COUNT(*) FROM produtos;")
    count = cur.fetchone()[0]

    if count == 0:
        produtos_iniciais = [
            ("X-Burger", 15.00, "Lanches"),
            ("X-Salada", 17.00, "Lanches"),
            ("Refrigerante Lata", 6.00, "Bebidas"),
            ("Batata Frita", 10.00, "Acompanhamentos"),
            ("Combo Completo", 35.00, "Combos")
        ]
        cur.executemany(
            "INSERT INTO produtos (descricao, preco, categoria) VALUES (%s, %s, %s);",
            produtos_iniciais
        )
        print("🍔 Produtos iniciais inseridos!")

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Banco inicializado com sucesso!")

# Função para listar produtos (agora com categoria!)
def listar_produtos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, descricao, preco, categoria FROM produtos ORDER BY categoria, id;")
    produtos = [
        {"id": r[0], "descricao": r[1], "preco": float(r[2]), "categoria": r[3] or "Outros"}
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return produtos

# CRUD clientes
def buscar_cliente_cpf(cpf):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT cpf, nome, telefone, endereco FROM clientes WHERE cpf = %s;", (cpf,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"cpf": row[0], "nome": row[1], "telefone": row[2], "endereco": row[3]}
    return None

def inserir_cliente(cpf, nome, telefone, endereco):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clientes (cpf, nome, telefone, endereco) VALUES (%s, %s, %s, %s) ON CONFLICT (cpf) DO NOTHING;",
        (cpf, nome, telefone, endereco)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Cliente {nome} salvo no banco!")

# Inserir pedido + itens
def inserir_pedido(cpf, itens, total):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO pedidos (cliente_cpf, total) VALUES (%s, %s) RETURNING id;", (cpf, total))
        pedido_id = cur.fetchone()[0]

        for item in itens:
            produto_id = item.get("id")
            qtd = item.get("quantidade", 1)
            subtotal = float(item.get("subtotal", 0))
            cur.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, subtotal) VALUES (%s, %s, %s, %s);",
                (pedido_id, produto_id, qtd, subtotal)
            )

        conn.commit()
        print(f"🧾 Pedido {pedido_id} salvo com sucesso!")
        return pedido_id

    except Exception as e:
        conn.rollback()
        print(f"⚠️ Erro ao salvar pedido: {e}")
        return None
    finally:
        cur.close()
        conn.close()

# Listar pedidos
def listar_pedidos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, c.nome, p.total, p.status, p.data_hora
        FROM pedidos p
        LEFT JOIN clientes c ON p.cliente_cpf = c.cpf
        ORDER BY p.data_hora DESC;
    """)
    pedidos = [
        {"id": r[0], "cliente": r[1], "total": float(r[2]), "status": r[3], "data_hora": r[4].strftime("%d/%m %H:%M")}
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return pedidos

# Atualizar status
def atualizar_status(pedido_id, novo_status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE pedidos SET status = %s WHERE id = %s;", (novo_status, pedido_id))
    conn.commit()
    cur.close()
    conn.close()