import json
import urllib.request
import urllib.error

# URLs das funções Lambda (copiadas do console da AWS)
URL_CADASTRAR = "https://sd4hffhvqbyrxuakvwvi5vl66q0wgwhu.lambda-url.us-east-1.on.aws/"
URL_PEDIDO = "https://xvwcywyfeuzouzrvrndczmjgbe0awncb.lambda-url.us-east-1.on.aws/"


def chamar_lambda(url, dados):
    """Envia os dados em JSON para a URL da Lambda e devolve a resposta."""
    corpo = json.dumps(dados).encode("utf-8")
    requisicao = urllib.request.Request(
        url,
        data=corpo,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requisicao) as resposta:
            return json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        return f"Erro {erro.code}: {erro.read().decode('utf-8')}"
    except urllib.error.URLError as erro:
        return f"Não foi possível conectar: {erro.reason}"


def pedir_livro():
    print("\n--- Pedir um livro ---")
    id_livro = input("Código do livro: ").strip()
    email = input("Seu e-mail: ").strip()
    while "@" not in email or "." not in email:
        print("E-mail inválido. Tente de novo.")
        email = input("Seu e-mail: ").strip()

    resposta = chamar_lambda(URL_PEDIDO, {"idLivro": id_livro, "emailCliente": email})

    if "avisado" in resposta:
        print("Livro disponível! Enviamos um e-mail para você ir à livraria efetivar a compra.")
    elif "pendente" in resposta:
        print("Livro indisponível no momento. Você receberá um e-mail quando ele chegar.")
    else:
        print(resposta)


def cadastrar_chegada():
    print("\n--- Cadastrar chegada de livro (colaborador) ---")
    id_livro = input("Código do livro: ").strip()
    titulo = input("Título: ").strip()
    autor = input("Autor: ").strip()

    while True:
        try:
            quantidade = int(input("Quantidade de exemplares: "))
            if quantidade > 0:
                break
            print("A quantidade precisa ser maior que zero.")
        except ValueError:
            print("Digite um número inteiro.")

    resposta = chamar_lambda(URL_CADASTRAR, {
        "idLivro": id_livro,
        "titulo": titulo,
        "autor": autor,
        "quantidade": quantidade,
    })
    print(resposta)


def main():
    while True:
        print("\n===== Sebo =====")
        print("1 - Pedir um livro (cliente)")
        print("2 - Cadastrar chegada de livro (colaborador)")
        print("0 - Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            pedir_livro()
        elif opcao == "2":
            cadastrar_chegada()
        elif opcao == "0":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
