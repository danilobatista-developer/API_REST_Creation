import requests

# URL do endpoint de token
token_url = "http://127.0.0.1:8000/token"


def get_token(username: str, password: str):
    # Configurar os dados da requisição
    data = {
        "username": username,
        "password": password
    }

    # Enviar a requisição POST para obter o token
    response = requests.post(token_url, data=data)

    # Verificar se a requisição foi bem-sucedida
    response.raise_for_status()

    # Retornar o token
    return response.json()


def main():
    username = "testuser"  # Substitua pelo nome de usuário válido
    password = "testpassword"  # Substitua pela senha válida

    # Obter o token
    try:
        token_response = get_token(username, password)
        print(f"Token recebido: {token_response}")

        # Usar o token para criar um veículo (exemplo)
        veiculo_url = "http://127.0.0.1:8000/veiculos"
        headers = {
            "Authorization": f"Bearer {token_response['access_token']}",
            "Content-Type": "application/json"
        }
        veiculo_data = {
            "modelo": "Fiat Uno",
            "ano": 2022,
            "placa": "ABC1234",
            "status": "disponível"
        }
        response = requests.post(veiculo_url, json=veiculo_data, headers=headers)
        print(f"Resposta ao criar veículo: {response.json()}")

    except requests.exceptions.HTTPError as e:
        print(f"Erro ao obter token ou criar veículo: {e}")


if __name__ == "__main__":
    main()
