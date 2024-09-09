import requests

# URL do endpoint de token
token_url = "http://127.0.0.1:8000/token"
# URL do endpoint de veículos
veiculo_url = "http://127.0.0.1:8000/veiculos"

def get_token(username: str, password: str):
    """
    Obtém um token de acesso JWT usando o nome de usuário e senha fornecidos.
    """
    data = {
        "username": username,
        "password": password
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()

def criar_veiculo(token: str, marca: str, modelo: str, ano: int, placa: str, status: str):
    """
    Cria um novo veículo usando o token de acesso JWT.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    veiculo_data = {
        "marca": marca,
        "modelo": modelo,
        "ano": ano,
        "placa": placa,
        "status": status
    }
    response = requests.post(veiculo_url, json=veiculo_data, headers=headers)
    return response

def main():
    username = "usuario_teste"  # Nome de usuário válido
    password = "teste12345"     # Senha válida

    try:
        token_response = get_token(username, password)
        print(f"Token recebido: {token_response}")

        # Teste de criação de veículo
        try:
            response = criar_veiculo(
                token=token_response['access_token'],
                marca="Fiat",
                modelo="Uno",
                ano=2022,
                placa="ABC1234",
                status="CONNECTADO"  # Status corrigido
            )
            response.raise_for_status()
            print(f"Resposta ao criar veículo: {response.json()}")
        except requests.exceptions.HTTPError as e:
            print(f"Erro ao criar veículo: {e}")

    except requests.exceptions.HTTPError as e:
        print(f"Erro ao obter token: {e}")

if __name__ == "__main__":
    main()
