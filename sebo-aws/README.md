# Sebo na AWS

Trabalho 2 de INF1304 – Distribuição e Concorrência (PUC-Rio, 2026/2).

Sistema de um sebo em que o cliente pede um livro e recebe um e-mail quando ele está disponível. Se o livro não estiver no estoque, o pedido fica registrado e o cliente é avisado automaticamente quando um colaborador cadastrar a chegada do livro.

O backend roda na AWS (Learner Lab, região **us-east-1**, conta **9870-1453-0538**). As interfaces rodam no computador do usuário e chamam o backend pela internet.

## Arquitetura

| Componente | Serviço | Disparado por | Função |
|---|---|---|---|
| `cadastrarLivro` | Lambda | Web (URL da função) | Registra a chegada de livros e soma a quantidade no estoque |
| `fazerPedido` | Lambda | Web (URL da função) | Consulta o estoque. Se houver, envia e-mail; senão, registra o pedido como pendente |
| `notificarClientes` | Lambda | Evento interno (DynamoDB Stream da tabela `Livros`) | Quando um livro passa de 0 para mais de 0 exemplares, avisa os clientes com pedido pendente |
| `Livros` | DynamoDB | – | Estoque. Chave de partição: `idLivro` |
| `Pedidos` | DynamoDB | – | Pedidos. Chave de partição: `idLivro`, chave de classificação: `emailCliente`, atributo `status` (`pendente` / `avisado`) |
| `AvisosLivraria` | SNS (tópico padrão) | – | Envia os e-mails. Cada assinatura tem uma política de filtro, para que cada cliente receba só os próprios avisos |

## Estrutura do repositório

```
├── index.html                 interface web
├── interface/sebo_cli.py      interface de linha de comando
└── lambdas/                   código das três funções Lambda
    ├── cadastrarLivro.py
    ├── fazerPedido.py
    └── notificarClientes.py
```

## Instalação

> Na conta **9870-1453-0538**, toda a aplicação já está instalada e configurada. Para usá-la, basta seguir a seção **Operação**. Os passos abaixo descrevem como reproduzir a instalação do zero em outra conta.

### 1. Banco de dados (DynamoDB)

1. Criar a tabela **`Livros`** com chave de partição `idLivro` (String).
2. Criar a tabela **`Pedidos`** com chave de partição `idLivro` (String) e chave de classificação `emailCliente` (String).
3. Na tabela `Livros`, em **Exportações e streams**, ativar o **Stream do DynamoDB** com o tipo de visualização **Imagens novas e antigas**.

### 2. E-mail (SNS)

1. Criar um tópico do tipo **Padrão** chamado **`AvisosLivraria`** e anotar o ARN.
2. Para cada cliente, criar uma assinatura com protocolo **E-mail** e ativar a **política de filtro**, com escopo **Atributos da mensagem**:

   ```json
   { "emailCliente": ["email.do@cliente.com"] }
   ```

3. O cliente precisa clicar no link **Confirm subscription** do e-mail que a AWS envia.

### 3. Funções Lambda

Para cada arquivo da pasta `lambdas/`:

1. Criar uma função com o mesmo nome, runtime **Python** e, em *Configurações adicionais → Personalizar perfil de execução*, o perfil **LabRole** (o Learner Lab não permite criar perfis novos).
2. Colar o código do arquivo e clicar em **Deploy**.
3. Em `fazerPedido.py` e `notificarClientes.py`, conferir se a constante `TOPICO_ARN` é o ARN do tópico criado.

Configurações extras:

- **`cadastrarLivro` e `fazerPedido`**: em *Configuração → URL da função*, criar uma URL com autenticação **NONE** e CORS com origem `*`, cabeçalho `content-type` e método `POST`.
- **`notificarClientes`**: na tabela `Livros`, em *Exportações e streams → Gatilhos*, criar um gatilho apontando para essa função.

### 4. Interfaces

Nas interfaces, as constantes `URL_CADASTRAR` e `URL_PEDIDO` devem conter as URLs das funções `cadastrarLivro` e `fazerPedido`:

- **Linha de comando**: no início de `interface/sebo_cli.py`. Precisa apenas de Python 3, sem bibliotecas extras.
- **Web**: no `<script>` de `index.html`. Não precisa instalar nada.

## Operação

### Antes de usar: ligar o lab e conferir o gatilho

1. No AWS Academy, abrir o **Learner Lab** e clicar em **Start Lab**. Esperar a bolinha ao lado de "AWS" ficar verde.
2. **Conferir se o gatilho do Stream está ativo.** Quando o lab fica desligado, a AWS bloqueia o acesso ao Stream e o gatilho da `notificarClientes` é desativado automaticamente. Sem ele, os clientes com pedido pendente não recebem o aviso.
   - Abrir a Lambda **`notificarClientes`** → **Configuração** → **Gatilhos**.
   - Se o estado estiver **Disabled**, selecionar o gatilho, clicar em **Editar**, marcar **Ativar gatilho** e salvar.
   - Atualizar a página e confirmar que o estado ficou **Enabled**.

As mudanças feitas na tabela enquanto o gatilho estava desligado não se perdem: o Stream guarda os eventos por 24 horas, e eles são processados quando o gatilho volta.

### Interface de linha de comando

```bash
python3 interface/sebo_cli.py
```

```
===== Sebo =====
1 - Pedir um livro (cliente)
2 - Cadastrar chegada de livro (colaborador)
0 - Sair
```

- **Opção 1**: informar o código do livro e o e-mail. Se houver estoque, o e-mail chega na hora. Se não, o pedido fica pendente.
- **Opção 2**: informar código, título, autor e quantidade. Se alguém estava esperando por esse livro, recebe o aviso por e-mail em alguns segundos.

### Interface web

Abrir o `index.html` no navegador (dois cliques no arquivo, ou `open index.html` no terminal do Mac) ou acessar a versão publicada no GitHub Pages.

- Aba **Sou cliente**: pedir um livro.
- Aba **Sou da livraria**: cadastrar a chegada de um livro.

### Exemplo de uso completo

1. Cliente pede o livro `L010`, que ainda não existe → mensagem de **indisponível**, pedido fica `pendente`.
2. Colaborador cadastra `L010` com quantidade 1.
3. Em alguns segundos, o cliente recebe o e-mail "Seu livro chegou no sebo" e o pedido passa para `avisado`.

O cliente só recebe e-mails se o endereço estiver inscrito e confirmado no tópico `AvisosLivraria`.

## Limitações conhecidas

- As URLs das funções usam autenticação **NONE**: qualquer pessoa com o endereço consegue chamá-las. Foi uma escolha para simplificar as interfaces neste trabalho.
- O gatilho do Stream é desativado quando o Learner Lab fica desligado e precisa ser religado manualmente (ver *Operação*).
- Cada cliente precisa ser inscrito no tópico manualmente, pelo console da AWS.