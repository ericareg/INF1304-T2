"""Lambda cadastrarLivro: o colaborador registra a chegada de livros no estoque.

Disparada pela web, pela URL da função (POST com JSON).
"""
import json
import boto3

dynamodb = boto3.resource('dynamodb')
tabela = dynamodb.Table('Livros')

def lambda_handler(event, context):
    """Grava o livro na tabela Livros e soma a quantidade ao estoque.

    Se o livro já existe, a quantidade é somada à atual; se não existe,
    a linha é criada. A mudança na tabela gera um evento no Stream, que
    dispara a Lambda notificarClientes.

    Entrada (JSON): idLivro, titulo, autor, quantidade.
    Saída: statusCode 200 e uma mensagem de confirmação.
    """
    if 'body' in event:
        dados = json.loads(event['body'])
    else:
        dados = event

    id_livro = dados['idLivro']
    quantidade = int(dados['quantidade'])

    tabela.update_item(
        Key={'idLivro': id_livro},
        UpdateExpression='SET titulo = :t, autor = :a ADD quantidade :q',
        ExpressionAttributeValues={
            ':t': dados['titulo'],
            ':a': dados['autor'],
            ':q': quantidade
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps(f'Livro {id_livro} cadastrado/atualizado')
    }