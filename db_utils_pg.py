# db_utils_pg.py
import psycopg2
from datetime import datetime

# 🔧 Conexão com o banco (Render)
def get_conn():
    return psycopg2.connect(
        host="dpg-d43e2ommcj7s73b062jg-a.oregon-postgres.render.com",
        dbname="halldb",
        user="halldb_user",
        password="dCu5hXO8okI8Qz0j9LK9i7AcZI3LYND0"
    )

# 🧱 Inicializa tabelas
def inicializar_banco():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            cpf VARCHAR(14) UNIQUE NOT NULL,
            telefone VARCHAR(20),
            endereco TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER REFERENCES clientes(id),
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total NUMERIC(10,2),
            status VARCHAR(20) DEFAULT 'Pendente'
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER REFERENCES pedidos(id),
            descricao TEXT,
            quantidade INTEGER,
            preco_unit NUMERIC(10,2)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Banco PostgreSQL inicializado com sucesso!")


# 👤 Buscar cliente pelo CPF
def buscar_cliente_cpf(cpf):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, telefone, endereco FROM clientes WHERE cpf = %s;", (cpf,))
    cliente = cur.fetchone()
    cur.close()
    conn.close()
    if cliente:
        return {
            'id': cliente[0],
            'nome': cliente[1],
            'telefone': cliente[2],
            'endereco': cliente[3]
        }
    return None


# 💾 Inserir novo cliente
def inserir_cliente(cpf, nome, telefone, endereco):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clientes (cpf, nome, telefone, endereco)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (cpf) DO NOTHING;
    """, (cpf, nome, telefone, endereco))
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Cliente {nome} ({cpf}) salvo no banco!")


# 🧾 Inserir pedido e itens vinculados ao cliente
def inserir_pedido(cpf, itens, total):
    conn = get_conn()
    cur = conn.cursor()

    # Busca ID do cliente pelo CPF
    cur.execute("SELECT id FROM clientes WHERE cpf = %s;", (cpf,))
    cliente = cur.fetchone()
    if not cliente:
        raise Exception("Cliente não encontrado para o CPF informado.")
    cliente_id = cliente[0]

    # Cria o pedido
    cur.execute(
        "INSERT INTO pedidos (cliente_id, total) VALUES (%s, %s) RETURNING id;",
        (cliente_id, total)
    )
    pedido_id = cur.fetchone()[0]

    # Adiciona os itens
    for item in itens:
        descricao = item.get('descricao', '')
        quantidade = item.get('quantidade', 1)
        preco_unit = item.get('preco', 0)
        cur.execute("""
            INSERT INTO itens_pedido (pedido_id, descricao, quantidade, preco_unit)
            VALUES (%s, %s, %s, %s);
        """, (pedido_id, descricao, quantidade, preco_unit))

    conn.commit()
    cur.close()
    conn.close()
    print(f"🧾 Pedido {pedido_id} salvo com sucesso!")
    return pedido_id


# 📋 Listar pedidos (para o painel)
def listar_pedidos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, c.cpf, p.data_hora, p.total, p.status
        FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id
        ORDER BY p.id DESC;
    """)
    pedidos = []
    for row in cur.fetchall():
        pedidos.append({
            'id': row[0],
            'cpf': row[1],
            'data_hora': row[2].strftime('%d/%m/%Y %H:%M'),
            'total': float(row[3]),
            'status': row[4]
        })
    cur.close()
    conn.close()
    return pedidos


# 🔁 Atualizar status
def atualizar_status(pid, novo_status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE pedidos SET status = %s WHERE id = %s;", (novo_status, pid))
    conn.commit()
    cur.close()
    conn.close()
    print(f"🔄 Status do pedido {pid} atualizado para '{novo_status}'")

# 🍕 Lista de produtos fixos
def listar_produtos():
    return [
        {"id": 1, "descricao": "X-Burger", "preco": 15.0},
        {"id": 2, "descricao": "X-Salada", "preco": 17.0},
        {"id": 3, "descricao": "Refrigerante Lata", "preco": 6.0},
        {"id": 4, "descricao": "Batata Frita", "preco": 10.0},
        {"id": 5, "descricao": "Combo Completo", "preco": 35.0}
    ]