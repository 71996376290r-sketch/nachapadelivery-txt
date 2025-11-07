import os
from datetime import datetime
import psycopg2

# -----------------------------------------
# CONFIGURAÇÕES BÁSICAS
# -----------------------------------------
BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

CLIENTES_FILE = os.path.join(DATA_DIR, 'clientes.txt')
PEDIDOS_FILE = os.path.join(DATA_DIR, 'pedidos.txt')

# -----------------------------------------
# CONEXÃO COM O BANCO (PostgreSQL)
# -----------------------------------------
def conectar_banco():
    try:
        conn = psycopg2.connect(
            host="dpg-d43e2ommcj7s73b062jg-a.oregon-postgres.render.com",
            database="halldb",
            user="halldb_user",
            password="dCu5hXO8okI8Qz0j9LK9i7AcZI3LYND0",
            port="5432",
            connect_timeout=3  # evita travar se o servidor estiver fora
        )
        return conn
    except Exception:
        return None  # retorna None se não conseguir conectar


def inicializar_banco():
    conn = conectar_banco()
    if not conn:
        print("⚠️ Banco indisponível, usando modo arquivo.")
        return

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            cpf VARCHAR(20) PRIMARY KEY,
            nome VARCHAR(100),
            telefone VARCHAR(30),
            endereco VARCHAR(200)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            cpf VARCHAR(20) REFERENCES clientes(cpf),
            data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total NUMERIC(10,2),
            status VARCHAR(30) DEFAULT 'Recebido'
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
# FUNÇÕES AUXILIARES PARA ARQUIVOS
# -----------------------------------------
def _read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return [l.rstrip('\n') for l in f if l.strip()]


def salvar_cliente_txt(cpf, nome, telefone, endereco):
    existing = buscar_cliente_cpf(cpf)
    if existing:
        return existing
    with open(CLIENTES_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{cpf}|{nome}|{telefone}|{endereco}\n")
    return {'cpf': cpf, 'nome': nome, 'telefone': telefone, 'endereco': endereco}


def salvar_pedido_txt(cpf, itens, total):
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    itens_str = ', '.join([f"{it['nome']} x{it['qtd']} (R${float(it['preco']):.2f})" for it in itens])
    with open(PEDIDOS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{cpf}|{data_hora}|{itens_str}|R${float(total):.2f}|Recebido\n")
    return len(_read_lines(PEDIDOS_FILE))


def buscar_cliente_cpf(cpf):
    cpf = (cpf or '').strip()
    for line in _read_lines(CLIENTES_FILE):
        parts = line.split('|')
        if parts and parts[0] == cpf:
            return {'cpf': parts[0], 'nome': parts[1], 'telefone': parts[2], 'endereco': parts[3] if len(parts) > 3 else ''}
    return None


# -----------------------------------------
# FUNÇÕES HÍBRIDAS (BANCO + BACKUP)
# -----------------------------------------
def inserir_cliente(cpf, nome, telefone, endereco):
    conn = conectar_banco()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO clientes (cpf, nome, telefone, endereco)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (cpf) DO UPDATE SET
                nome=EXCLUDED.nome, telefone=EXCLUDED.telefone, endereco=EXCLUDED.endereco;
            """, (cpf, nome, telefone, endereco))
            conn.commit()
            cur.close()
            conn.close()
            print(f"✅ Cliente {nome} salvo no banco!")
            return {'cpf': cpf, 'nome': nome, 'telefone': telefone, 'endereco': endereco}
        except Exception as e:
            print("⚠️ Erro ao salvar cliente no banco, salvando em arquivo:", e)
            return salvar_cliente_txt(cpf, nome, telefone, endereco)
    else:
        print("⚠️ Banco indisponível, salvando cliente em arquivo.")
        return salvar_cliente_txt(cpf, nome, telefone, endereco)


def inserir_pedido(cpf, itens, total):
    conn = conectar_banco()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO pedidos (cpf, total) VALUES (%s, %s) RETURNING id;", (cpf, total))
            pedido_id = cur.fetchone()[0]
            for it in itens:
                cur.execute("""
                    INSERT INTO itens_pedido (pedido_id, produto_nome, quantidade, preco_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (pedido_id, it['nome'], it['qtd'], it['preco']))
            conn.commit()
            cur.close()
            conn.close()
            print(f"✅ Pedido #{pedido_id} salvo no banco!")
            return pedido_id
        except Exception as e:
            print("⚠️ Erro ao salvar pedido no banco, salvando em arquivo:", e)
            return salvar_pedido_txt(cpf, itens, total)
    else:
        print("⚠️ Banco indisponível, salvando pedido em arquivo.")
        return salvar_pedido_txt(cpf, itens, total)


# -----------------------------------------
# EXEMPLO DE USO
# -----------------------------------------
if __name__ == "__main__":
    inicializar_banco()

    cliente = inserir_cliente("12345678900", "João Silva", "11999999999", "Rua A, 123")

    pedido = [
        {"nome": "Hall Burger", "qtd": 2, "preco": 25.00},
        {"nome": "Refrigerante", "qtd": 1, "preco": 6.00}
    ]
    inserir_pedido(cliente["cpf"], pedido, total=56.00)