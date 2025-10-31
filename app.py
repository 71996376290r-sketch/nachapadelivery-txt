import os, webbrowser, threading
from flask import Flask, render_template, request, redirect, url_for, jsonify
import db_utils_txt_pipe as db

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verificar_cpf', methods=['POST'])
def verificar_cpf():
    cpf = request.form.get('cpf','').strip()
    cliente = db.buscar_cliente_cpf(cpf)
    if cliente:
        produtos = db.listar_produtos()
        return render_template('pedido.html', cliente=cliente, produtos=produtos)
    else:
        return redirect(url_for('cadastro', cpf=cpf))

@app.route('/cadastro')
def cadastro():
    cpf = request.args.get('cpf','')
    return render_template('cadastro.html', cpf=cpf)

@app.route('/salvar_cliente', methods=['POST'])
def salvar_cliente():
    nome = request.form.get('nome')
    cpf = request.form.get('cpf','').strip()
    telefone = request.form.get('telefone','')
    endereco = request.form.get('endereco','')
    cliente = db.inserir_cliente(cpf, nome, telefone, endereco)
    produtos = db.listar_produtos()
    return render_template('pedido.html', cliente=cliente, produtos=produtos)

@app.route('/salvar_pedido', methods=['POST'])
def salvar_pedido():
    data = request.get_json() or request.form
    cpf = data.get('cpf') or data.get('id_cliente') or ''
    try:
        cpf = str(cpf)
    except:
        cpf = ''
    itens = data.get('itens') or []
    total = 0.0
    if isinstance(itens, str):
        import json
        itens = json.loads(itens)
    for it in itens:
        total += float(it.get('preco',0)) * int(it.get('qtd',0))
    pedido_id = db.inserir_pedido(cpf, itens, total)
    return jsonify({'status':'ok','pedido_id': pedido_id, 'mensagem':'Pedido salvo (TXT) com sucesso!'})

@app.route('/confirmacao/<int:pid>')
def confirmacao(pid):
    return render_template('confirmacao.html', pedido_id=pid)

def open_browser():
    try:
        webbrowser.open('http://127.0.0.1:5000')
    except:
        pass
from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

# Caminhos dos arquivos TXT
CLIENTES_TXT = "clientes.txt"
PEDIDOS_TXT = "pedidos.txt"

def ler_pedidos():
    pedidos = []
    if os.path.exists(PEDIDOS_TXT):
        with open(PEDIDOS_TXT, "r", encoding="utf-8") as f:
            for linha in f:
                partes = linha.strip().split("|")
                if len(partes) == 5:
                    pedidos.append({
                        "nome": partes[0],
                        "cpf": partes[1],
                        "itens": partes[2],
                        "total": partes[3],
                        "status": partes[4]
                    })
    return pedidos

def salvar_pedidos(pedidos):
    with open(PEDIDOS_TXT, "w", encoding="utf-8") as f:
        for p in pedidos:
            f.write(f"{p['nome']}|{p['cpf']}|{p['itens']}|{p['total']}|{p['status']}\n")

@app.route("/painel")
def painel():
    pedidos = ler_pedidos()
    return render_template("painel.html", pedidos=pedidos)

@app.route("/atualizar_status", methods=["POST"])
def atualizar_status():
    cpf = request.form["cpf"]
    novo_status = request.form["status"]

    pedidos = ler_pedidos()
    for p in pedidos:
        if p["cpf"] == cpf:
            p["status"] = novo_status
            break

    salvar_pedidos(pedidos)
    return redirect("/painel")

if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
