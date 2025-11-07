import psycopg2
from psycopg2 import sql
from datetime import datetime

DB_URL = "postgresql://halldb_user:dCu5hXO8okI8Qz0j9LK9i7AcZI3LYND0@dpg-d43e2ommcj7s73b062jg-a/halldb"

def conectar():
    return psycopg2.connect(DB_URL)

def inicializar_banco():
    conn = conectar()
    cur = conn.cursor()

    # 🧍 Clientes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            cpf VARCHAR(14) UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            telefone TEXT,
            endereco TEXT
        );
    """)

    # 🧾 Pedidos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER REFERENCES clientes(id),
            total NUMERIC(10,2),
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 🧺 Itens do pedido
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedido_itens (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER REFERENCES pedidos(id),
            produto_id INTEGER,
            quantidade INTEGER,
            preco_unit NUMERIC(10,2)
        );
    """)

    # 🛠️ Corrige ou recria tabela produtos se estiver com estrutura antiga
    try:
        cur.execute("SELECT id, nome, preco FROM produtos LIMIT 1;")
    except psycopg2.Error:
        print("⚙️ Corrigindo estrutura da tabela produtos...")

        cur.execute("DROP TABLE IF EXISTS produtos CASCADE;")
        cur.execute("""
            CREATE TABLE produtos (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco NUMERIC(10,2) NOT NULL,
                categoria TEXT DEFAULT 'Outros',
                imagem TEXT
            );
        """)

        # 👇 Insere alguns produtos padrão pra facilitar teste
        cur.executemany("""
            INSERT INTO produtos (nome, descricao, preco, categoria, imagem) VALUES (%s, %s, %s, %s, %s);
        """, [
            ('X-Burger', 'Pão, carne, queijo e maionese da casa', 18.00, 'Lanches', 'img/xburger.jpg'),
            ('X-Salada', 'Pão, carne, queijo, alface, tomate e maionese', 20.00, 'Lanches', 'img/xsalada.jpg'),
            ('Coca-Cola Lata', '350ml bem gelada', 6.00, 'Bebidas', 'img/coca.jpg'),
            ('Batata Frita', 'Porção média crocante', 12.00, 'Acompanhamentos', 'img/batata.jpg'),
            ('Brownie', 'Chocolate com calda', 10.00, 'Sobremesas', 'img/brownie.jpg')
        ])

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Banco inicializado com sucesso!")

# 🧍 Inserir ou atualizar cliente
def inserir_cliente(cpf, nome, telefone, endereco):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clientes (cpf, nome, telefone, endereco)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (cpf) DO UPDATE SET nome = EXCLUDED.nome;
    """, (cpf, nome, telefone, endereco))
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Cliente {nome} salvo no banco!")

# 🔍 Buscar cliente por CPF
def buscar_cliente_cpf(cpf):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, telefone, endereco FROM clientes WHERE cpf = %s;", (cpf,))
    c = cur.fetchone()
    cur.close()
    conn.close()
    return {'id': c[0], 'nome': c[1], 'telefone': c[2], 'endereco': c[3]} if c else None

# 💾 Inserir pedido
def inserir_pedido(cpf, itens, total):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT id FROM clientes WHERE cpf = %s;", (cpf,))
    c = cur.fetchone()
    if not c:
        print("❌ Cliente não encontrado.")
        return None
    cliente_id = c[0]

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

# 📋 Listar pedidos
def listar_pedidos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, c.nome, p.total, p.data_hora
        FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id
        ORDER BY p.data_hora DESC;
    """)
    pedidos = [{'id': r[0], 'cliente': r[1], 'total': float(r[2]), 'data': r[3].strftime("%d/%m %H:%M")} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return pedidos

# 🍔 Listar produtos (com categoria)
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