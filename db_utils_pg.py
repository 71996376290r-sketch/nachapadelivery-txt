import psycopg2
from psycopg2 import sql
from datetime import datetime

DB_URL = "postgresql://halldb_user:dCu5hXO8okI8Qz0j9LK9i7AcZI3LYND0@dpg-d43e2ommcj7s73b062jg-a/halldb"

def conectar():
    return psycopg2.connect(DB_URL)

def inicializar_banco():
    conn = conectar()
    cur = conn.cursor()

    # Tabela de clientes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            cpf VARCHAR(14) UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            telefone TEXT,
            endereco TEXT
        );
    """)

    # Tabela de produtos (agora com categoria)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco NUMERIC(10,2) NOT NULL,
            categoria TEXT DEFAULT 'Outros',
            imagem TEXT
        );
    """)

    # Tabela de pedidos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER REFERENCES clientes(id),
            total NUMERIC(10,2),
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Tabela itens do pedido
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedido_itens (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER REFERENCES pedidos(id),
            produto_id INTEGER REFERENCES produtos(id),
            quantidade INTEGER,
            preco_unit NUMERIC(10,2)
        );
    """)

    # 🛠️ Corrige se faltar a coluna 'categoria'
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='produtos' AND column_name='categoria'
            ) THEN
                ALTER TABLE produtos ADD COLUMN categoria TEXT DEFAULT 'Outros';
            END IF;
        END $$;
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Banco inicializado com sucesso!")

def inserir_cliente(cpf, nome, telefone, endereco):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (cpf, nome, telefone, endereco) VALUES (%s, %s, %s, %s) ON CONFLICT (cpf) DO NOTHING;", 
                (cpf, nome, telefone, endereco))
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Cliente {nome} salvo no banco!")

def buscar_cliente_cpf(cpf):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, telefone, endereco FROM clientes WHERE cpf = %s;", (cpf,))
    cliente = cur.fetchone()
    cur.close()
    conn.close()
    if cliente:
        return {'id': cliente[0], 'nome': cliente[1], 'telefone': cliente[2], 'endereco': cliente[3]}
    return None

def inserir_pedido(cpf, itens, total):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT id FROM clientes WHERE cpf = %s;", (cpf,))
    cliente = cur.fetchone()
    if not cliente:
        print("❌ Cliente não encontrado.")
        return None
    cliente_id = cliente[0]

    cur.execute("INSERT INTO pedidos (cliente_id, total) VALUES (%s, %s) RETURNING id;", (cliente_id, total))
    pedido_id = cur.fetchone()[0]

    for item in itens:
        cur.execute("""
            INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, preco_unit)
            VALUES (%s, %s, %s, %s);
        """, (pedido_id, item['id'], item['qtd'], item['preco']))

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Pedido {pedido_id} salvo com sucesso!")
    return pedido_id

def listar_pedidos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, c.nome, p.total, p.data_hora
        FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id
        ORDER BY p.data_hora DESC;
    """)
    pedidos = [{'id': row[0], 'cliente': row[1], 'total': float(row[2]), 'data': row[3].strftime("%d/%m %H:%M")} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return pedidos

def listar_produtos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome, preco, COALESCE(categoria, 'Outros'), imagem 
        FROM produtos 
        ORDER BY categoria, nome;
    """)
    produtos = [{'id': r[0], 'nome': r[1], 'preco': float(r[2]), 'categoria': r[3], 'imagem': r[4]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return produtos