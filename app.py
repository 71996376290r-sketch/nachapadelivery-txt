@app.route('/')
def home():
    return redirect(url_for('pedido'))

@app.route('/pedido')
def pedido():
    produtos = Produto.query.all()
    return render_template('pedido.html', produtos=produtos)

@app.route('/confirmar_cpf', methods=['POST'])
def confirmar_cpf():
    cpf = request.form['cpf']
    pedido_json = request.form['pedido_json']

    cliente = Cliente.query.filter_by(cpf=cpf).first()
    if cliente:
        # Cliente existe → salva o pedido direto
        pedido_dados = json.loads(pedido_json)
        novo_pedido = Pedido(cliente_id=cliente.id, itens=pedido_dados)
        db.session.add(novo_pedido)
        db.session.commit()
        return render_template('sucesso.html', cliente=cliente)

    # Cliente não existe → redireciona para cadastro
    return redirect(url_for('cadastro', cpf=cpf, pedido_json=pedido_json))

@app.route('/cadastro')
def cadastro():
    cpf = request.args.get('cpf')
    pedido_json = request.args.get('pedido_json')
    return render_template('cadastro.html', cpf=cpf, pedido_json=pedido_json)

@app.route('/salvar_cliente', methods=['POST'])
def salvar_cliente():
    nome = request.form['nome']
    cpf = request.form['cpf']
    telefone = request.form['telefone']
    endereco = request.form['endereco']
    pedido_json = request.form.get('pedido_json')

    cliente = Cliente(nome=nome, cpf=cpf, telefone=telefone, endereco=endereco)
    db.session.add(cliente)
    db.session.commit()

    # Depois de cadastrar, salva o pedido
    if pedido_json:
        pedido_dados = json.loads(pedido_json)
        novo_pedido = Pedido(cliente_id=cliente.id, itens=pedido_dados)
        db.session.add(novo_pedido)
        db.session.commit()

    return render_template('sucesso.html', cliente=cliente)