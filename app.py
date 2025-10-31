from flask import Flask, render_template, request, redirect, url_for
import db_utils_txt_pipe as db

app = Flask(__name__)

# ==========================
# ROTA PRINCIPAL - CPF
# ==========================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar_cliente', methods=['POST'])
def buscar_cliente():
    cpf = request.form['cpf'].strip()
    cliente = db.buscar_cliente_cpf(cpf)
    if cliente:
        produtos = db.listar_produtos()
        return render_template('pedido.html', cliente=cliente, produtos=produtos)
    else:
        return render_template('cadastro.html', cpf=cpf)

# ==========================
# CADASTRO DE CLIENTE
# ==========================
@app.route('/salvar_cliente', methods=['POST'])
def salvar_cliente():
    nome = request.form['nome']
    cpf = request.form.get('cpf', '')
    telefone = request.form['telefone']
    endereco = request.form['endereco']

    db.inserir_cliente(nome, cpf, telefone, endereco)
    cliente = db.buscar_cliente_cpf(cpf)
    produtos = db.listar_produtos()
    return render_template('pedido.html', cliente=cliente, produtos=produtos)

# ==========================
# FAZER PEDIDO
# ==========================
@app.route('/fazer_pedido', methods=['POST'])
def fazer_pedido():
    cpf = request.form['cpf']
    nome = request.form['nome']
    itens = request.form['itens']
    total = float(request.form['total'])

    db.inserir_pedido(nome, cpf, itens, total)
    return render_template('confirmacao.html', nome=nome, total=total)

# ==========================
# PAINEL DO CAIXA
# ==========================
@app.route('/painel')
def painel():
    pedidos = db.carregar_pedidos()
    return render_template('painel.html', pedidos=pedidos)

# ==========================
# ATUALIZAR STATUS DO PEDIDO
# ==========================
@app.route('/atualizar_status/<int:index>/<status>')
def atualizar_status(index, status):
    db.atualizar_status_pedido(index, status)
    return redirect(url_for('painel'))

# ==========================
# EXECUÇÃO LOCAL
# ==========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)