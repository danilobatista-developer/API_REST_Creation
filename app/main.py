from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from contextlib import asynccontextmanager

from . import models, database, schemas, auth
from .auth import get_current_active_user, authenticate_user, create_access_token

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização: criar tabelas
    print("App startup - Inicializando banco de dados...")
    models.Base.metadata.create_all(bind=database.engine)
    yield
    # Encerramento
    print("App shutdown - Encerrando...")

app = FastAPI(
    title="API de Gerenciamento de Veículos",
    description="API para gerenciar usuários e veículos. Inclui endpoints para autenticação, criação e manipulação de veículos. Desenvolvido por Danilo Batista (linkedin.com/in/danilobatistadeveloper).",
    version="1.0.0",
    lifespan=lifespan
)

# Dependência para obter o banco de dados
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para login e geração de token
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    **Descrição:**
    Endpoint para login e geração de um token JWT.

    **Parâmetros:**
    - `username`: Nome de usuário.
    - `password`: Senha do usuário.

    **Resposta:**
    - `200 OK` com um token de acesso JWT e o tipo do token.

    **Exemplo de Request:**
    ```json
    {
        "username": "example_user",
        "password": "example_password"
    }
    ```

    **Exemplo de Resposta:**
    ```json
    {
        "access_token": "your_access_token",
        "token_type": "bearer"
    }
    ```

    **Exemplo de Implementação em Python:**
    ```python
    import httpx

    async def get_token(username: str, password: str):
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8000/token", data={"username": username, "password": password})
            return response.json()

    # Exemplo de uso
    import asyncio
    token = asyncio.run(get_token("example_user", "example_password"))
    print(token)
    ```
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para criar novos usuários
@app.post("/usuarios/", response_model=schemas.Usuario)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """
    **Descrição:**
    Endpoint para criar um novo usuário.

    **Parâmetros:**
    - `username`: Nome de usuário.
    - `password`: Senha do usuário.

    **Resposta:**
    - `200 OK` com os detalhes do usuário criado.

    **Exemplo de Request:**
    ```json
    {
        "username": "new_user",
        "password": "new_password"
    }
    ```

    **Exemplo de Resposta:**
    ```json
    {
        "username": "new_user"
    }
    ```

    **Exemplo de Implementação em Python:**
    ```python
    import httpx

    async def create_user(username: str, password: str, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8000/usuarios/", json={"username": username, "password": password}, headers=headers)
            return response.json()

    # Exemplo de uso
    import asyncio
    token = "your_access_token"  # Primeiro obtenha o token
    user = asyncio.run(create_user("new_user", "new_password", token))
    print(user)
    ```
    """
    hashed_password = auth.get_password_hash(usuario.password)
    db_usuario = models.Usuario(username=usuario.username, hashed_password=hashed_password)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# Endpoint raiz
@app.get("/")
def read_root():
    """
    **Descrição:**
    Endpoint raiz que retorna uma mensagem de boas-vindas.

    **Resposta:**
    - `200 OK` com uma mensagem de boas-vindas.

    **Exemplo de Resposta:**
    ```json
    {"message": "Bem-vindo à API de gerenciamento de veículos!"}
    ```

    **Exemplo de Implementação em Python:**
    ```python
    import httpx

    async def get_root():
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/")
            return response.json()

    # Exemplo de uso
    import asyncio
    message = asyncio.run(get_root())
    print(message)
    ```
    """
    return {"message": "Bem-vindo à API de gerenciamento de veículos!"}

# Endpoints de veículos - somente usuários autenticados podem acessar
@app.get("/veiculos", response_model=List[schemas.Veiculo])
def listar_veiculos(db: Session = Depends(get_db), current_user: schemas.Usuario = Depends(get_current_active_user)):
    """
    **Descrição:**
    Endpoint para listar todos os veículos. Apenas usuários autenticados podem acessar este endpoint.

    **Resposta:**
    - `200 OK` com uma lista de veículos.

    **Exemplo de Resposta:**
    ```json
    [
        {"id": 1, "modelo": "Fusca", "ano": 1968, "status": "disponível"},
        {"id": 2, "modelo": "Civic", "ano": 2020, "status": "em manutenção"}
    ]
    ```

    **Exemplo de Implementação em Python:**
    ```python
    import httpx

    async def list_vehicles(token: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/veiculos", headers=headers)
            return response.json()

    # Exemplo de uso
    import asyncio
    token = "your_access_token"  # Primeiro obtenha o token
    vehicles = asyncio.run(list_vehicles(token))
    print(vehicles)
    ```
    """
    veiculos = db.query(models.Veiculo).all()
    return veiculos

@app.post("/veiculos", response_model=schemas.Veiculo)
def criar_veiculo(veiculo: schemas.VeiculoCreate, db: Session = Depends(get_db), current_user: schemas.Usuario = Depends(get_current_active_user)):
    """
    **Descrição:**
    Endpoint para criar um novo veículo. Apenas usuários autenticados podem acessar este endpoint.

    **Parâmetros:**
    - `modelo`: Modelo do veículo.
    - `ano`: Ano do veículo.
    - `status`: Status do veículo.

    **Resposta:**
    - `200 OK` com os detalhes do veículo criado.

    **Exemplo de Request:**
    ```json
    {
        "modelo": "Civic",
        "ano": 2022,
        "status": "disponível"
    }
    ```

    **Exemplo de Resposta:**
    ```json
    {
        "id": 3,
        "modelo": "Civic",
        "ano": 2022,
        "status": "disponível"
    }
    ```

    **Exemplo de Implementação em Python:**
    ```python
    import httpx

    async def create_vehicle(modelo: str, ano: int, status: str, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        data = {"modelo": modelo, "ano": ano, "status": status}
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8000/veiculos", json=data, headers=headers)
            return response.json()

    # Exemplo de uso
    import asyncio
    token = "your_access_token"  # Primeiro obtenha o token
    vehicle = asyncio.run(create_vehicle("Civic", 2022, "disponível", token))
    print(vehicle)
    ```
    """
    db_veiculo = models.Veiculo(**veiculo.model_dump())  # Utilizando model_dump() no lugar de dict()
    db.add(db_veiculo)
    db.commit()
    db.refresh(db_veiculo)
    return db_veiculo

@app.get("/veiculos/{veiculo_id}", response_model=schemas.Veiculo)
def obter_veiculo(veiculo_id: int, db: Session = Depends(get_db), current_user: schemas.Usuario = Depends(get_current_active_user)):
    """
    **Descrição:**
    Endpoint para obter detalhes de um veículo pelo seu ID. Apenas usuários autenticados podem acessar este endpoint.

    **Parâmetros:**
    - `veiculo_id`: ID do veículo.

    **Resposta:**
    - `200 OK` com os detalhes do veículo.

    **Exemplo de Resposta:**
    ```json
    {
        "id": 1,
        "modelo": "Fusca",
        "ano": 1968,
        "status": "disponível"
    }
    ```

    **Exemplo de Implementação em Python:**
    ```python
    import httpx

    async def get_vehicle(veiculo_id: int, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:8000/veiculos/{veiculo_id}", headers=headers)
            return response.json()

    # Exemplo de uso
    import asyncio
    token = "your_access_token"  # Primeiro obtenha o token
    vehicle = asyncio.run(get_vehicle(1, token))
    print(vehicle)
    ```
    """
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo

@app.put("/veiculos/{veiculo_id}", response_model=schemas.Veiculo)
def atualizar_status(veiculo_id: int, status: str, db: Session = Depends(get_db), current_user: schemas.Usuario = Depends(get_current_active_user)):
    """
    **Descrição:**
    Endpoint para atualizar o status de um veículo pelo seu ID. Apenas usuários autenticados podem acessar este endpoint.

    **Parâmetros:**
    - `veiculo_id`: ID do veículo.
    - `status`: Novo status do veículo.

    **Resposta:**
    - `200 OK` com os detalhes do veículo atualizado.

    **Exemplo de Request:**
    ```json
    {
        "status": "CONNECTADO"
    }
    ```

    **Exemplo de Resposta:**
    ```json
    {
        "id": 1,
        "modelo": "Fusca",
        "ano": 1968,
        "status": "em manutenção"
    }
    ```

    **Exemplo de Implementação em Python:**
    ```python
    import httpx

    async def update_vehicle_status(veiculo_id: int, status: str, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        params = {"status": status}
        async with httpx.AsyncClient() as client:
            response = await client.put(f"http://127.0.0.1:8000/veiculos/{veiculo_id}", params=params, headers=headers)
            return response.json()

    # Exemplo de uso
    import asyncio
    token = "your_access_token"  # Primeiro obtenha o token
    vehicle = asyncio.run(update_vehicle_status(1, "em manutenção", token))
    print(vehicle)
    ```
    """
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    veiculo.status = status
    db.commit()
    db.refresh(veiculo)
    return veiculo

@app.delete("/veiculos/{veiculo_id}")
def excluir_veiculo(veiculo_id: int, db: Session = Depends(get_db), current_user: schemas.Usuario = Depends(get_current_active_user)):
    """
    **Descrição:**
    Endpoint para excluir um veículo pelo seu ID. Apenas usuários autenticados podem acessar este endpoint.

    **Parâmetros:**
    - `veiculo_id`: ID do veículo.

    **Resposta:**
    - `200 OK` com uma mensagem de sucesso.

    **Exemplo de Resposta:**
    ```json
    {"message": "Veículo excluído com sucesso"}
    ```

    **Exemplo de Implementação em Python:**
    ```python
    import httpx

    async def delete_vehicle(veiculo_id: int, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"http://127.0.0.1:8000/veiculos/{veiculo_id}", headers=headers)
            return response.json()

    # Exemplo de uso
    import asyncio
    token = "your_access_token"  # Primeiro obtenha o token
    result = asyncio.run(delete_vehicle(1, token))
    print(result)
    ```
    """
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    db.delete(veiculo)
    db.commit()
    return {"message": "Veículo excluído com sucesso"}
