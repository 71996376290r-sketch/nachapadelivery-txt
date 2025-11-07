import os, webbrowser, threading, json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import db_utils_pg as db

# 🧱 Inicializa o banco (cria tabelas e produtos se faltar algo)
db.inicializar_banco()

app = Flask(__name__)
app.secret_key = 'nachapa2025'  # Necessário para sessão

# 🏠 Tela inicial agora é o pedido direto
@app.route('/')
def index():
    produtos = db.listar_produtos()
    return render_template('pedido.html', produtos=produtos)

# 🧾 Rota que salva o pedido temporariamente e redireciona pra CPF
@app.route('/salvar_pedido', methods=['POST'])
def salvar_pedido():
    data = request.get_json() or {}
    itens = data.get('itens') or []
    total = data.get('total') or 0.0

    # Guarda pedido temporariamente na sessão
    session['pedido_temp'] = {'itens': itens, 'total': total}
    return jsonify({'redirect': url_for('cpf_page')})

# 📄 Tela de CPF (antigo index.html)
@app.route('/cpf')
def cpf_page():
    return render_template('index.html')

# 🔍 Verifica CPF — se existir, salva pedido; se não, vai pra cadastro
@app.route('/verificar_cpf', methods=['POST'])
def verificar_cpf():
    cpf = request.form.get('cpf', '').strip()
    pedido_data = session.get('pedido_temp')

    if not pedido_data:
        return "Erro: pedido não encontrado na sessão.", 400

    cliente = db.buscar_cliente_cpf(cpf)
    if cliente:
        # Cliente existe → salva pedido
        itens = pedido_data.get('itens', [])
        total = float(pedido_data.get('total', 0))
        pedido_id = db.inserir_pedido(cpf, itens, total)
        session.pop('pedido_temp', None)
        return redirect(url_for('confirmacao', pid=pedido_id))
    else:
        # Cliente não existe → vai pra tela de cadastro
        session['cpf_cadastro'] = cpf
        return redirect(url_for('cadastro'))

# 👤 Tela de cadastro
@app.route('/cadastro')
def cadastro():
    cpf = session.get('cpf_cadastro', '')
    return render_template('cadastro.html', cpf=cpf)

# 💾 Salva novo cliente e o pedido (se houver)
@app.route('/salvar_cliente', methods=['POST'])
def salvar_cliente():
    nome = request.form.get('nome')
    cpf = request.form.get('cpf', '').strip()
    telefone = request.form.get('telefone', '')
    endereco = request.form.get('endereco', '')

    db.inserir_cliente(cpf, nome, telefone, endereco)

    # Se ainda houver pedido pendente → salva agora
    pedido_data = session.pop('pedido_temp', None)
    if pedido_data:
        itens = pedido_data.get('itens', [])
        total = float(pedido_data.get('total', 0))
        pedido_id = db.inserir_pedido(cpf, itens, total)
        return redirect(url_for('confirmacao', pid=pedido_id))

    return redirect(url_for('index'))

# ✅ Tela de confirmação
@app.route('/confirmacao/<int:pid>')
def confirmacao(pid):
    return render_template('confirmacao.html', pedido_id=pid)

# 📋 Painel administrativo
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
    db.atualizar_status(pid, novo_status)
    return redirect(url_for('painel'))

# 🚀 Abrir automaticamente no navegador
def open_browser():
    try:
        webbrowser.open('http://127.0.0.1:5000')
    except:
        pass


if __name__ == '__main__':
    db.inicializar_banco()
    threading.Timer(1.0, open_browser).start()
    db.inicializar_banco()
    app.run(host='0.0.0.0', port=5000, debug=True)
