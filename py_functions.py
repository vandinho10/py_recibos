from datetime import *
import os, random, re, sqlite3

db = sqlite3.connect('database.db')

def run_query(query, params=()):
    cursor = db.cursor()
    cursor.execute(query, params)
    return cursor.fetchall()

def inserir_fornecedor():
    nome = input('Nome do fornecedor: ')
    cnpj = input('CNPJ: ')
    endereco = input('Endereço: ')
    cidade = input('Cidade: ')
    uf = input('Estado: ')
    
    query = 'INSERT INTO fornecedores (nome, cnpj, endereco, cidade, uf) VALUES (?, ?, ?, ?, ?)'
    run_query(query, (nome, cnpj, endereco, cidade, uf))
    db.commit()
    print('Fornecedor inserido com sucesso!')

def listar_fornecedores():
    query = 'SELECT * FROM fornecedores'
    rows = run_query(query)
    
    if rows:
        print('\n>> Fornecedores:')
        for row in rows:
            print(f'>> ID: {row[0]}, CNPJ: {row[2]}, Estado: {row[5]}, Cidade: {row[4]}, Nome: {row[1]}')
    else:
        print('Nenhum fornecedor cadastrado.')

def inserir_item():
    nome = input('Nome do item: ')
    query = 'INSERT INTO itens (nome) VALUES (?)'
    run_query(query, (nome,))
    db.commit()
    print('Item inserido com sucesso!')

def listar_itens():
    query = 'SELECT * FROM itens'
    rows = run_query(query)
    
    if rows:
        print('\n>> Itens:')
        for row in rows:
            print(f'>> ID: {row[0]}, Nome: {row[1]}')
    else:
        print('Nenhum item cadastrado.')

def gerar_numero_recibo():
    # prefixo = "#"
    numero_aleatorio = random.randint(1, 1000000)
    # return f'{prefixo}{numero_aleatorio}'
    return f'{numero_aleatorio}'

def emitir_recibo():
    recibo = {
        'num_recibo': gerar_numero_recibo(),
        'fornecedor': None,
        'data': None,
        'itens': []
    }

    data_hoje = datetime.now().strftime('%d/%m/%Y')

    fornecedor_id = input('ID do fornecedor: ')
    data = input(f'Data do Recibo (em branco para {data_hoje}): ') or data_hoje
    recibo['data'] = data

    fornecedor = buscar_fornecedor(fornecedor_id)
    
    if fornecedor:
        recibo['fornecedor'] = fornecedor[0][0]
        adicionar_itens_ao_recibo(recibo, fornecedor_id)
    else:
        print('Fornecedor não encontrado.')

def buscar_fornecedor(fornecedor_id):
    query = 'SELECT nome FROM fornecedores WHERE id = ?'
    return run_query(query, (fornecedor_id,))

def buscar_item(item_id):
    query = 'SELECT nome FROM itens WHERE id = ?'
    return run_query(query, (item_id,))

def adicionar_itens_ao_recibo(recibo, fornecedor_id):
    def adicionar_item():
        item_id = input('Insira o ID do item ou "sair" para concluir o recibo: ')
        if item_id.lower() == 'sair':
            finalizar_recibo(recibo, fornecedor_id)
        elif not item_id:
            print('Nenhum ID de item fornecido. Tente novamente.')
            adicionar_item()
        else:
            item = buscar_item(item_id)
            if item:
                quantidade = float(input('Quantidade: ').replace(',', '.'))
                preco = float(input('Preço: ').replace(',', '.'))
                recibo['itens'].append({'itemId': item_id, 'nome': item[0][0], 'quantidade': quantidade, 'preco': preco})
                adicionar_item()
            else:
                print('Item não encontrado. Tente novamente.')
                adicionar_item()

    adicionar_item()

def finalizar_recibo(recibo, fornecedor_id):
    print('\nRecibo:')
    print(f'Fornecedor: {fornecedor_id} {recibo["fornecedor"]}')
    print(f'Número do Recibo: {recibo["num_recibo"]}')
    print(f'Data: {recibo["data"]}')
    print('Itens:')
    total_recibo = 0

    for i, item in enumerate(recibo['itens']):
        total_item = round(item['quantidade'] * item['preco'], 2)
        print(f'Item {i + 1}: {item["itemId"]} {item["nome"]} - Qtde: {item["quantidade"]} - Preço: {item["preco"]} - Total do Item: {total_item}')
        total_recibo += total_item

    print(f'Total do Recibo: {total_recibo:.2f}')

    inserir_recibo(fornecedor_id, recibo['num_recibo'], recibo['data'], recibo['itens'])

def inserir_recibo(fornecedor_id, num_recibo, data, recibo_itens):
    total_recibo = 0

    for item in recibo_itens:
        total_recibo += round(item['quantidade'] * item['preco'], 2)

    query_recibo = 'INSERT INTO recibos (num_recibo, fornecedor_id, data, total) VALUES (?, ?, ?, ?)'
    run_query(query_recibo, (num_recibo, fornecedor_id, data, total_recibo))
    db.commit()

    for item in recibo_itens:
        query_itens_recibo = 'INSERT INTO itens_recibo (recibo_id, item_id, quantidade, preco) VALUES (?, ?, ?, ?)'
        run_query(query_itens_recibo, (num_recibo, item['itemId'], item['quantidade'], item['preco']))
        db.commit()

    gerar_html_recibo(num_recibo)
    print('Recibo inserido com sucesso!')


def gerar_html_recibo(numero_recibo=None):
    if not numero_recibo:
        numero_recibo = input('Informe o número do recibo para salvar em HTML: ')
        # numero_recibo = '#' + numero_recibo

    query_recibo = '''
    SELECT recibos.num_recibo, recibos.data, recibos.total, fornecedores.nome AS nome_fornecedor, fornecedores.cnpj, fornecedores.endereco, fornecedores.cidade, fornecedores.uf
    FROM recibos
    JOIN fornecedores ON recibos.fornecedor_id = fornecedores.id
    WHERE recibos.num_recibo = ?
    '''

    dados_recibo = run_query(query_recibo, (numero_recibo,))

    query_itens_recibo = '''
    SELECT itens.nome AS nome_item, itens_recibo.quantidade, itens_recibo.preco
    FROM itens_recibo
    JOIN itens ON itens_recibo.item_id = itens.id
    WHERE itens_recibo.recibo_id = ?
    '''

    dados_itens_recibo = run_query(query_itens_recibo, (numero_recibo,))

    if dados_recibo and dados_itens_recibo:
        date_string = dados_recibo[0][1]
        date_obj = datetime.strptime(date_string, '%d/%m/%Y')  # Converte a string em um objeto 'datetime'
        numbers_from_dados_recibo = ''.join(re.findall(r'\d+', dados_recibo[0][4])) # Mantem somente os numeros no CNPJ

        file_name = f"recibo_{date_obj.strftime('%Y%m%d')}_{numbers_from_dados_recibo}_{numero_recibo}.html"
        directory_path = os.getcwd()+'\\recibos'
        output_path = os.path.join(directory_path, file_name)

        try:
            os.makedirs(directory_path, exist_ok=True)

            html_content = f'''
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Recibo {numero_recibo}</title>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
                    <style>
                        .bordered-container {{
                            border: 2px solid #000; /* Adicione o estilo de borda desejado */
                            padding: 10px; /* Adicione um preenchimento para separar a borda do conteúdo */
                            max-width: 450px;
                            margin: 0 auto;
                        }}
                    </style>
                </head>
            
                <body>
                    <div class="bordered-container">
                        <div class="row">
                            <table class="table table-borderless table-sm">
                                <tbody>
                                    <tr>
                                        <td style="font-weight: normal; width: 50%; text-align: right;"><p class="mb-0">{dados_recibo[0][1]}</p></th>
                                        <td style="font-weight: bold; width: 50%; text-align: center;"><p class="mb-0">#{numero_recibo}</p></th>
                                    </tr>
                                    <tr>
                                        <td colspan="2" style="text-align: center; font-weight: bold;"><p class="mb-0">{dados_recibo[0][3]}</p></td>
                                    </tr>
                                    <tr>
                                        <td colspan="2" style="text-align: center;"><p class="mb-0">{dados_recibo[0][5]}</p></td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight: normal;  text-align: right;"><p class="mb-0">{dados_recibo[0][6]}/{dados_recibo[0][7]}</p></th>
                                        <td style="font-weight: normal;  text-align: left;"><p class="mb-0">{dados_recibo[0][4]}</p></th>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th style="width: 48%;">Item</th>
                                    <th style="width: 5%;">Qtde</th>
                                    <th style="width: 22%;">Preço</th>
                                    <th style="width: 25%;">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                            {''.join(f'<tr><td>{item[0]}</td><td>{item[1]}</td><td>R$ {item[2]:.2f}</td><td>R$ {item[1] * item[2]:.2f}</td></tr>' for item in dados_itens_recibo)}
                                <tr>
                                    <td colspan="3" align="right"><strong>Total:</strong></td>
                                    <td style="text-align: left"><p><strong>R$ {dados_recibo[0][2]:.2f}</strong></p></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
                </body>
            </html>
            '''

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f'Arquivo HTML gerado: {file_name}')
        except Exception as e:
            print(f'Erro ao gerar o arquivo HTML do recibo: {str(e)}')
    else:
        print('Dados do recibo não encontrados.')
