# Sebo na AWS — Trabalho 2 de Distribuição e Concorrência (2026/2)

Aplicação de um sebo usando AWS Lambda, DynamoDB e SNS (AWS Academy Learner Lab, região us-east-1).

## Estrutura

- `lambdas/cadastrarLivro.py` — colaborador registra a chegada de livros (URL da função)
- `lambdas/fazerPedido.py` — cliente pede um livro; avisa por e-mail se houver estoque, senão deixa pendente (URL da função)
- `lambdas/notificarClientes.py` — disparada pelo Stream da tabela Livros; avisa quem estava esperando quando o livro chega
- `interface/sebo_cli.py` — interface de linha de comando

## Como rodar a interface

Requer Python 3 (sem bibliotecas extras):

    python3 interface/sebo_cli.py
