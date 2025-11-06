import psycopg2
from psycopg2 import sql

# -----------------------------------------
# Função de conexão e criação das tabelas
# -----------------------------------------
def conectar_banco():
    conn = psycopg2.connect(
Server [localhost]: dpg-d43e2ommcj7s73b062jg-a.oregon-postgres.render.com
Database [postgres]: halldb
Port [5432]: 
Username [postgres]: halldb_user
Password for user halldb_user: dCu5hXO8okI8Qz0j9LK9i7AcZI3LYND0
    )
    return conn






def inicializar_banco():
    conn = conectar_banco()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            cliente_nome VARCHAR(100),
            data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total NUMERIC(10,2)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id SERIAL PRIMARY KEY,
            pedido_id INT REFERENCES pedidos(id) ON DELETE CASCADE,
            produto_nome VARCHAR(100),
            quantidade INT,
            preco_unitario NUMERIC(10,2)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Banco inicializado com sucesso!")


# -----------------------------------------
# Função para salvar pedido e itens
# -----------------------------------------
def salvar_pedido(cliente, itens):
    """
    cliente: string
    itens: lista de dicionários, ex:
        [
            {"produto": "Pizza Calabresa", "quantidade": 2, "preco": 39.90},
            {"produto": "Refrigerante", "quantidade": 1, "preco": 8.00}
        ]
    """
    conn = None
    try:
        conn = conectar_banco()
        cur = conn.cursor()

        # Calcula total
        total = sum(item["quantidade"] * item["preco"] for item in itens)

        # Insere pedido
        cur.execute(
            "INSERT INTO pedidos (cliente_nome, total) VALUES (%s, %s) RETURNING id",
            (cliente, total)
        )
        pedido_id = cur.fetchone()[0]

        # Insere itens
        for item in itens:
            cur.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_nome, quantidade, preco_unitario) VALUES (%s, %s, %s, %s)",
                (pedido_id, item["produto"], item["quantidade"], item["preco"])
            )

        conn.commit()
        print(f"✅ Pedido salvo com sucesso! ID: {pedido_id}")

    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ Erro ao salvar o pedido:", e)

    finally:
        if conn:
            cur.close()
            conn.close()


# -----------------------------------------
# Função para listar pedidos e itens
# -----------------------------------------
def listar_pedidos():
    conn = conectar_banco()
    cur = conn.cursor()

    cur.execute("SELECT id, cliente_nome, data_pedido, total FROM pedidos ORDER BY id DESC;")
    pedidos = cur.fetchall()

    for pedido in pedidos:
        print(f"\n📦 Pedido #{pedido[0]} - Cliente: {pedido[1]} - Total: R$ {pedido[3]:.2f} - Data: {pedido[2]}")
        cur.execute("SELECT produto_nome, quantidade, preco_unitario FROM itens_pedido WHERE pedido_id = %s;", (pedido[0],))
        itens = cur.fetchall()
        for item in itens:
            print(f"   🧾 {item[0]} (x{item[1]}) - R$ {item[2]:.2f}")

    cur.close()
    conn.close()


# -----------------------------------------
# Exemplo de uso
# -----------------------------------------
if __name__ == "__main__":
    inicializar_banco()  # cria as tabelas se não existirem

    pedido = [
        {"produto": "Pizza Margherita", "quantidade": 1, "preco": 42.00},
        {"produto": "Suco de Laranja", "quantidade": 2, "preco": 7.50}
    ]
    salvar_pedido("João Silva", pedido)

    listar_pedidos()
