import os, webbrowser, threading
from flask import Flask, render_template, request, redirect, url_for, jsonify
import db_utils_txt_pipe as db

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('pedido.html')

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
@app.route('/painel')
def painel():
    pedidos = []
    for i, line in enumerate(db._read_lines(db.PEDIDOS_FILE), start=1):
        parts = line.split('|')
        if len(parts) >= 5:
            pedidos.append({
                'id': i,
                'cpf': parts[0],
                'data_hora': parts[1],
                'itens': parts[2],
                'total': parts[3],
                'status': parts[4]
            })
    return render_template('painel.html', pedidos=pedidos)

@app.route('/alterar_status/<int:pid>', methods=['POST'])
def alterar_status(pid):
    novo_status = request.form.get('status')
    ok = db.atualizar_status(pid, novo_status)
    return redirect(url_for('painel'))

def open_browser():
    try:
        webbrowser.open('http://127.0.0.1:5000')
    except:
        pass

if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
