import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Conexão com o banco de dados PostgreSQL
def get_connection():
    return psycopg2.connect(
        host="dpg-d43e2ommcj7s73b062jg-a.oregon-postgres.render.com",
        dbname="halldb",
        user="halldb_user",
        password="dCu5hXO8okI8Qz0j9LK9i7AcZI3LYND0"
    )

@app.route('/salvar_pedido', methods=['POST'])
def salvar_pedido():
    data = request.get_json()
    nome = data.get('nome')
    cpf = data.get('cpf')
    total = data.get('total')

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 1️⃣ Salvar ou buscar cliente
        cur.execute("SELECT id FROM clientes WHERE cpf = %s;", (cpf,))
        cliente = cur.fetchone()

        if cliente:
            cliente_id = cliente[0]
            print(f"✅ Cliente já existe: ID {cliente_id}")
        else:
            cur.execute(
                "INSERT INTO clientes (nome, cpf) VALUES (%s, %s) RETURNING id;",
                (nome, cpf)
            )
            cliente_id = cur.fetchone()[0]
            print(f"✅ Novo cliente salvo com ID {cliente_id}")

        # 2️⃣ Salvar o pedido vinculado ao cliente
        cur.execute(
            "INSERT INTO pedidos (cliente_id, total) VALUES (%s, %s) RETURNING id;",
            (cliente_id, total)
        )
        pedido_id = cur.fetchone()[0]
        conn.commit()

        print(f"✅ Pedido salvo com sucesso! ID: {pedido_id}")
        return jsonify({"mensagem": "Pedido salvo no banco com sucesso!"}), 200

    except Exception as e:
        print(f"⚠️ Erro ao salvar pedido no banco: {e}")
        return jsonify({"erro": str(e)}), 500

    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)