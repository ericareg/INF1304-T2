"""Lambda fazerPedido: o cliente pede um livro.

Disparada pela web, pela URL da função (POST com JSON).
"""
import json
import boto3

dynamodb = boto3.resource('dynamodb')
tabela_livros = dynamodb.Table('Livros')
tabela_pedidos = dynamodb.Table('Pedidos')
sns = boto3.client('sns')

TOPICO_ARN = 'arn:aws:sns:us-east-1:987014530538:AvisosLivraria'

def lambda_handler(event, context):
    """Consulta o estoque e registra o pedido do cliente.

    Se o livro tem quantidade maior que 0, publica um aviso no tópico SNS
    com o atributo emailCliente (o filtro da assinatura entrega o e-mail
    só a esse cliente) e grava o pedido como 'avisado'. Caso contrário,
    grava o pedido como 'pendente', para ser avisado pela notificarClientes.

    Entrada (JSON): idLivro, emailCliente.
    Saída: statusCode 200 e o status do pedido ('avisado' ou 'pendente').
    """
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