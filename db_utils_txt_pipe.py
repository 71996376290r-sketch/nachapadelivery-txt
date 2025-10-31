import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENTES_TXT = os.path.join(BASE_DIR, "clientes.txt")
PEDIDOS_TXT = os.path.join(BASE_DIR, "pedidos.txt")


# ==========================
# CLIENTES
# ==========================
def carregar_clientes():
    clientes = []
    if os.path.exists(CLIENTES_TXT):
        with open(CLIENTES_TXT, "r", encoding="utf-8") as f:
            for line in f:
                dados = line.strip().split("|")
                if len(dados) == 4:
                    nome, cpf, telefone, endereco = dados
                    clientes.append({
                        "nome": nome,
                        "cpf": cpf,
                        "telefone": telefone,
                        "endereco": endereco
                    })
    return clientes


def salvar_clientes(clientes):
    with open(CLIENTES_TXT, "w", encoding="utf-8") as f:
        for c in clientes:
            line = f"{c['nome']}|{c['cpf']}|{c['telefone']}|{c['endereco']}\n"
            f.write(line)


def buscar_cliente_cpf(cpf):
    clientes = carregar_clientes()
    for c in clientes:
        if c["cpf"] == cpf:
            return c
    return None


def inserir_cliente(nome, cpf, telefone, endereco):
    clientes = carregar_clientes()
    clientes.append({
        "nome": nome,
        "cpf": cpf,
        "telefone": telefone,
        "endereco": endereco
    })
    salvar_clientes(clientes)


# ==========================
# PRODUTOS
# ==========================
def listar_produtos():
    return [
        {"id": 1, "nome": "Hall Burger", "preco": 22.50, "categoria": "Burgers", "img": "/static/img/burgers/hallburger.jpg"},
        {"id": 2, "nome": "Big Cupim", "preco": 28.90, "categoria": "Burgers", "img": "/static/img/burgers/bigcupim.jpg"},
        {"id": 3, "nome": "Batata Frita", "preco": 10.00, "categoria": "Acompanhamentos", "img": "/static/img/acompanhamentos/batata.jpg"},
        {"id": 4, "nome": "Refrigerante", "preco": 6.00, "categoria": "Bebidas", "img": "/static/img/bebidas/refri.jpg"}
    ]


# ==========================
# PEDIDOS
# ==========================
def carregar_pedidos():
    pedidos = []
    if os.path.exists(PEDIDOS_TXT):
        with open(PEDIDOS_TXT, "r", encoding="utf-8") as f:
            for line in f:
                dados = line.strip().split("|")
                if len(dados) == 5:
                    nome, cpf, itens, total, status = dados
                    pedidos.append({
                        "nome": nome,
                        "cpf": cpf,
                        "itens": itens,
                        "total": float(total),
                        "status": status
                    })
    return pedidos


def salvar_pedidos(pedidos):
    with open(PEDIDOS_TXT, "w", encoding="utf-8") as f:
        for p in pedidos:
            line = f"{p['nome']}|{p['cpf']}|{p['itens']}|{p['total']}|{p['status']}\n"
            f.write(line)


def inserir_pedido(nome, cpf, itens, total):
    pedidos = carregar_pedidos()
    pedidos.append({
        "nome": nome,
        "cpf": cpf,
        "itens": itens,
        "total": total,
        "status": "Recebido"
    })
    salvar_pedidos(pedidos)


def atualizar_status_pedido(index, novo_status):
    pedidos = carregar_pedidos()
    if 0 <= index < len(pedidos):
        pedidos[index]["status"] = novo_status
        salvar_pedidos(pedidos)