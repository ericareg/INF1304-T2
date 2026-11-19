import json
import boto3

dynamodb = boto3.resource('dynamodb')
tabela_livros = dynamodb.Table('Livros')
tabela_pedidos = dynamodb.Table('Pedidos')
sns = boto3.client('sns')

TOPICO_ARN = 'arn:aws:sns:us-east-1:987014530538:AvisosLivraria'

def lambda_handler(event, context):
    if 'body' in event:
        dados = json.loads(event['body'])
    else:
        dados = event

    id_livro = dados['idLivro']
    email = dados['emailCliente']

    resposta = tabela_livros.get_item(Key={'idLivro': id_livro})
    livro = resposta.get('Item')

    if livro and livro['quantidade'] > 0:
        sns.publish(
            TopicArn=TOPICO_ARN,
            Subject='Livro disponivel no sebo',
            Message=f"O livro '{livro['titulo']}' está disponível. Compareça à livraria para efetivar a compra.",
            MessageAttributes={
                'emailCliente': {'DataType': 'String', 'StringValue': email}
            }
        )
        status = 'avisado'
    else:
        status = 'pendente'

    tabela_pedidos.put_item(Item={
        'idLivro': id_livro,
        'emailCliente': email,
        'status': status
    })

    return {
        'statusCode': 200,
        'body': json.dumps(f'Pedido registrado com status: {status}')
    }
