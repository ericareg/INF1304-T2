import json
import boto3

dynamodb = boto3.resource('dynamodb')
tabela = dynamodb.Table('Livros')

def lambda_handler(event, context):
    # Se veio pela web (URL da função), os dados chegam como texto em 'body'
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
