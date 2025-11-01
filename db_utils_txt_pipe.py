import os
from datetime import datetime

BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

CLIENTES_FILE = os.path.join(DATA_DIR, 'clientes.txt')
PEDIDOS_FILE = os.path.join(DATA_DIR, 'pedidos.txt')

def _read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return [l.rstrip('\n') for l in f if l.strip()]

def buscar_cliente_cpf(cpf):
    cpf = (cpf or '').strip()
    for line in _read_lines(CLIENTES_FILE):
        parts = line.split('|')
        if parts and parts[0] == cpf:
            return {'cpf': parts[0], 'nome': parts[1], 'telefone': parts[2], 'endereco': parts[3] if len(parts)>3 else ''}
    return None

def inserir_cliente(cpf, nome, telefone, endereco):
    cpf = (cpf or '').strip()
    existing = buscar_cliente_cpf(cpf) if cpf else None
    if existing:
        return existing
    line = f"{cpf}|{nome}|{telefone}|{endereco}\n"
    with open(CLIENTES_FILE, 'a', encoding='utf-8') as f:
        f.write(line)
    return {'cpf': cpf, 'nome': nome, 'telefone': telefone, 'endereco': endereco}

def listar_produtos():
    return [
        {'id':1, 'nome':'Hall Burger', 'categoria':'Burgers', 'preco':25.00, 'imagem':'static/img/burgers/hallburger.jpg'},
        {'id':2, 'nome':'Big Cupim', 'categoria':'Burgers', 'preco':28.00, 'imagem':'static/img/burgers/bigcupim.jpg'},
        {'id':3, 'nome':'Batata', 'categoria':'Acompanhamentos', 'preco':8.00, 'imagem':'static/img/acompanhamentos/batata.jpg'},
        {'id':4, 'nome':'Refrigerante', 'categoria':'Bebidas', 'preco':6.00, 'imagem':'static/img/bebidas/refri.jpg'},
    ]

def inserir_pedido(cpf, itens_list, total):
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    itens_str = ', '.join([f"{it['nome']} x{it['qtd']} (R${float(it['preco']):.2f})" for it in itens_list])
    line = f"{cpf}|{data_hora}|{itens_str}|R${float(total):.2f}|Recebido\n"
    with open(PEDIDOS_FILE, 'a', encoding='utf-8') as f:
        f.write(line)
    lines = _read_lines(PEDIDOS_FILE)
    return len(lines)
    
    
def atualizar_status(pedido_id, novo_status):
    linhas = _read_lines(PEDIDOS_FILE)
    if 0 < pedido_id <= len(linhas):
        partes = linhas[pedido_id - 1].split('|')
        if len(partes) < 5:
            partes.append(novo_status)
        else:
            partes[4] = novo_status
        linhas[pedido_id - 1] = '|'.join(partes)
        with open(PEDIDOS_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas) + '\n')
        return True
    return False
