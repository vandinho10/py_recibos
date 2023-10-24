# Autor: Vanderson Oliveira
# Versão: 0.0.2
# Descrição: Aplicação para geração de recibos com armazenamento.

from py_functions import *

def criar_tabelas():
    create_tables_queries = [
        'CREATE TABLE IF NOT EXISTS fornecedores (id INTEGER PRIMARY KEY, nome TEXT, cnpj TEXT, endereco TEXT, cidade TEXT, uf TEXT)',
        'CREATE TABLE IF NOT EXISTS itens (id INTEGER PRIMARY KEY, nome TEXT)',
        'CREATE TABLE IF NOT EXISTS recibos (id INTEGER PRIMARY KEY, num_recibo INTEGER, fornecedor_id INTEGER, data DATETIME, total REAL)',
        'CREATE TABLE IF NOT EXISTS itens_recibo (id INTEGER PRIMARY KEY, recibo_id INTEGER, item_id INTEGER, quantidade INTEGER, preco REAL)'
    ]

    for query in create_tables_queries:
        run_query(query)
        db.commit()

def menu_principal():
    while True:
        print()
        print('Escolha uma opção:')
        print('1. Inserir fornecedor')
        print('2. Inserir item')
        print('3. Listar fornecedores')
        print('4. Listar itens')
        print('5. Emitir recibo')
        print('6. Salvar HTML do recibo')
        print('7. Sair')

        opcao = input()

        if opcao == '1':
            inserir_fornecedor()
        elif opcao == '2':
            inserir_item()
        elif opcao == '3':
            listar_fornecedores()
        elif opcao == '4':
            listar_itens()
        elif opcao == '5':
            emitir_recibo()
        elif opcao == '6':
            gerar_html_recibo()
        elif opcao == '7':
            db.close()
            print('Saindo do programa.')
            break

def iniciar_app():
    criar_tabelas()
    menu_principal()

iniciar_app()
