from flask import Flask, render_template, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# -----------------------------
# 🔧 Conexão com o banco
# -----------------------------
def get_connection():
    return psycopg2.connect(
        host="dpg-d43e2ommcj7s73b062jg-a.oregon-postgres.render.com",
        dbname="halldb",
        user="halldb_user",
        password="dCu5hXO8okI8Qz0j9LK9i7AcZI3LYND0"
    )

# -----------------------------
# 🗃️ Inicializa o banco (se necessário)
# -----------------------------
def inicializar_banco():
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Cria tabela de clientes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                cpf VARCHAR(14) UNIQUE NOT NULL
            );
        """)

        # Cria tabela de pedidos
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER REFERENCES clientes(id),
                total NUMERIC(10,2) NOT NULL,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Banco inicializado com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro ao inicializar o banco: {e}")

# -----------------------------
# 🌐 Página principal
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

# -----------------------------
# 💾 Rota para salvar pedido
# -----------------------------
@app.route('/salvar_pedido', methods=['POST'])
def salvar_pedido():
    data = request.get_json()
    nome = data.get('nome')
    cpf = data.get('cpf')
    total = data.get('total')

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verifica se o cliente já existe
        cur.execute("SELECT id FROM clientes WHERE cpf = %s;", (cpf,))
        cliente = cur.fetchone()

        if cliente:
            cliente_id = cliente[0]
            print(f"👤 Cliente já existe: ID {cliente_id}")
        else:
            cur.execute(
                "INSERT INTO clientes (nome, cpf) VALUES (%s, %s) RETURNING id;",
                (nome, cpf)
            )
            cliente_id = cur.fetchone()[0]
            print(f"✅ Novo cliente salvo: ID {cliente_id}")

        # Salva o pedido vinculado ao cliente
        cur.execute(
            "INSERT INTO pedidos (cliente_id, total) VALUES (%s, %s) RETURNING id;",
            (cliente_id, total)
        )
        pedido_id = cur.fetchone()[0]
        conn.commit()

        print(f"🧾 Pedido salvo com sucesso! ID do pedido: {pedido_id}")
        return jsonify({"mensagem": "Pedido salvo no banco com sucesso!"}), 200

    except Exception as e:
        print(f"⚠️ Erro ao salvar pedido no banco: {e}")
        return jsonify({"erro": str(e)}), 500

    finally:
        if conn:
            cur.close()
            conn.close()

# -----------------------------
# 🚀 Inicializa app
# -----------------------------
if __name__ == '__main__':
    inicializar_banco()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)