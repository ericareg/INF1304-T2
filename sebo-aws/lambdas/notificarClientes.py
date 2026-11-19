import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
tabela_pedidos = dynamodb.Table('Pedidos')
sns = boto3.client('sns')

TOPICO_ARN = 'arn:aws:sns:us-east-1:987014530538:AvisosLivraria'

def lambda_handler(event, context):
    # O Stream pode mandar várias mudanças de uma vez
    for registro in event['Records']:
        if registro['eventName'] not in ('INSERT', 'MODIFY'):
            continue

        nova = registro['dynamodb']['NewImage']
        antiga = registro['dynamodb'].get('OldImage', {})

        qtd_nova = int(nova.get('quantidade', {'N': '0'})['N'])
        qtd_antiga = int(antiga.get('quantidade', {'N': '0'})['N'])

        if qtd_antiga > 0 or qtd_nova <= 0:
            continue

        id_livro = nova['idLivro']['S']
        titulo = nova['titulo']['S']

        pedidos = tabela_pedidos.query(
            KeyConditionExpression=Key('idLivro').eq(id_livro)
        )['Items']

        for pedido in pedidos:
            if pedido['status'] != 'pendente':
                continue

            sns.publish(
                TopicArn=TOPICO_ARN,
                Subject='Seu livro chegou no sebo',
                Message=f"O livro '{titulo}' que você pediu chegou! Compareça à livraria para efetivar a compra.",
                MessageAttributes={
                    'emailCliente': {'DataType': 'String', 'StringValue': pedido['emailCliente']}
                }
            )

            tabela_pedidos.update_item(
                Key={'idLivro': id_livro, 'emailCliente': pedido['emailCliente']},
                UpdateExpression='SET #s = :s',
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={':s': 'avisado'}
            )

    return {'statusCode': 200}
