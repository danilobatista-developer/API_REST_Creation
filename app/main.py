from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from contextlib import asynccontextmanager
from sqlalchemy.exc import IntegrityError

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
    - `username`: Nome de usuário (str).
    - `password`: Senha do usuário (str).

    **Resposta:**
    - 200 OK com um token de acesso JWT e o tipo do token.

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
    Cria um novo usuário no sistema. O usuário será criado com uma senha criptografada.

    **Parâmetros:**
    - `usuario`: Objeto contendo `username` e `password` para o novo usuário.

    **Resposta:**
    - 201 Created com os dados do usuário criado.

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
        "username": "new_user",
        "hashed_password": "$2b$12$..."
    }
    ```

    **Exemplo de Implementação em Python:**

    ```python
    import httpx

    async def create_user(username: str, password: str):
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8000/usuarios/", json={"username": username, "password": password})
            return response.json()

    # Exemplo de uso
    import asyncio
    user = asyncio.run(create_user("new_user", "new_password"))
    print(user)
    """
    hashed_password = auth.get_password_hash(usuario.password)
    db_usuario = models.Usuario(username=usuario.username, hashed_password=hashed_password)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


# Endpoint raiz
@app.get("/", summary="Endpoint raiz", description="Endpoint de boas-vindas à API.")
def read_root():
    """
    **Descrição:**
    Endpoint de boas-vindas à API.

    **Resposta:**
    - 200 OK com uma mensagem de boas-vindas.

    **Exemplo de Resposta:**

    ```json
    {
        "message": "Bem-vindo à API de gerenciamento de veículos!"
    }
    ```
    """
    return {"message": "Bem-vindo à API de gerenciamento de veículos!"}


# Endpoints de veículos - somente usuários autenticados podem acessar
@app.get("/veiculos", response_model=List[schemas.Veiculo], summary="Listagem de veículos",
         description="Lista todos os veículos registrados. Requer autenticação.")
def listar_veiculos(db: Session = Depends(get_db), current_user: schemas.Usuario = Depends(get_current_active_user)):
    """
    **Descrição:**
    Lista todos os veículos registrados no sistema.

    **Resposta:**
    - 200 OK com uma lista de veículos.

    **Exemplo de Resposta:**

    ```json
    [
        {
            "id": 1,
            "placa": "ABC1234",
            "status": "CONNECTADO"
        },
        {
            "id": 2,
            "placa": "XYZ5678",
            "status": "DESCONECTADO"
        }
    ]
    ```

    **Exemplo de Implementação em Python:**

    ```python
    import httpx

    async def list_vehicles(token: str):
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/veiculos", headers={"Authorization": f"Bearer {token}"})
            return response.json()

    # Exemplo de uso
    import asyncio
    vehicles = asyncio.run(list_vehicles("your_access_token"))
    print(vehicles)
    """
    veiculos = db.query(models.Veiculo).all()
    return veiculos


@app.post("/veiculos", response_model=schemas.Veiculo, summary="Criação de veículo",
          description="Cria um novo veículo no sistema. A placa deve ser única e o status deve ser 'CONNECTADO' ou 'DESCONECTADO'.")
def criar_veiculo(veiculo: schemas.VeiculoCreate, db: Session = Depends(get_db),
                  current_user: schemas.Usuario = Depends(get_current_active_user)):
    """
    **Descrição:**
    Cria um novo veículo no sistema. A placa deve ser única e o status deve ser 'CONNECTADO' ou 'DESCONECTADO'.

    **Parâmetros:**
    - `veiculo`: Objeto contendo `placa` e `status` do veículo.

    **Resposta:**
    - 201 Created com os dados do veículo criado.

    **Exemplo de Request:**

    ```json
    {
        "placa": "XYZ1234",
        "status": "CONNECTADO"
    }
    ```

    **Exemplo de Resposta:**

    ```json
    {
        "id": 3,
        "placa": "XYZ1234",
        "status": "CONNECTADO"
    }
    ```

    **Exemplo de Implementação em Python:**

    ```python
    import httpx

    async def create_vehicle(token: str, placa: str, status: str):
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8000/veiculos", json={"placa": placa, "status": status}, headers={"Authorization": f"Bearer {token}"})
            return response.json()

    # Exemplo de uso
    import asyncio
    vehicle = asyncio.run(create_vehicle("your_access_token", "XYZ1234", "CONNECTADO"))
    print(vehicle)
    """
    if veiculo.status not in ["CONNECTADO", "DESCONECTADO"]:
        raise HTTPException(status_code=400,
                            detail="Status inválido. O status deve ser 'CONNECTADO' ou 'DESCONECTADO'.")
    db_veiculo = models.Veiculo(**veiculo.model_dump())
    try:
        db.add(db_veiculo)
        db.commit()
        db.refresh(db_veiculo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Placa já registrada.")
    return db_veiculo


@app.get("/veiculos/{veiculo_id}", response_model=schemas.Veiculo, summary="Detalhes do veículo",
         description="Obtém os detalhes de um veículo específico pelo ID.")
def obter_veiculo(veiculo_id: int, db: Session = Depends(get_db),
                  current_user: schemas.Usuario = Depends(get_current_active_user)):
    """
    **Descrição:**
    Obtém os detalhes de um veículo específico pelo ID.

    **Parâmetros:**
    - `veiculo_id`: ID do veículo (int).

    **Resposta:**
    - 200 OK com os dados do veículo.
    - 404 Not Found se o veículo não for encontrado.

    **Exemplo de Request:**

    ```http
    GET /veiculos/1 HTTP/1.1
    ```

    **Exemplo de Resposta:**

    ```json
    {
        "id": 1,
        "placa": "ABC1234",
        "status": "CONNECTADO"
    }
    ```

    **Exemplo de Implementação em Python:**

    ```python
    import httpx

    async def get_vehicle(token: str, veiculo_id: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:8000/veiculos/{veiculo_id}", headers={"Authorization": f"Bearer {token}"})
            return response.json()

    # Exemplo de uso
    import asyncio
    vehicle = asyncio.run(get_vehicle("your_access_token", 1))
    print(vehicle)
    """
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo


@app.put("/veiculos/{veiculo_id}", response_model=schemas.Veiculo, summary="Atualização de status do veículo",
         description="Atualiza o status de um veículo existente. O status deve ser 'CONNECTADO' ou 'DESCONECTADO'.")
def atualizar_status(veiculo_id: int, status: str, db: Session = Depends(get_db),
                     current_user: schemas.Usuario = Depends(get_current_active_user)):
    """
    **Descrição:**
    Atualiza o status de um veículo existente. O status deve ser 'CONNECTADO' ou 'DESCONECTADO'.

    **Parâmetros:**
    - `veiculo_id`: ID do veículo (int).
    - `status`: Novo status do veículo (str).

    **Resposta:**
    - 200 OK com os dados do veículo atualizado.
    - 404 Not Found se o veículo não for encontrado.

    **Exemplo de Request:**

    ```http
    PUT /veiculos/1 HTTP/1.1
    Content-Type: application/json

    {
        "status": "DESCONECTADO"
    }
    ```

    **Exemplo de Resposta:**

    ```json
    {
        "id": 1,
        "placa": "ABC1234",
        "status": "DESCONECTADO"
    }
    ```

    **Exemplo de Implementação em Python:**

    ```python
    import httpx

    async def update_vehicle_status(token: str, veiculo_id: int, status: str):
        async with httpx.AsyncClient() as client:
            response = await client.put(f"http://127.0.0.1:8000/veiculos/{veiculo_id}", json={"status": status}, headers={"Authorization": f"Bearer {token}"})
            return response.json()

    # Exemplo de uso
    import asyncio
    vehicle = asyncio.run(update_vehicle_status("your_access_token", 1, "DESCONECTADO"))
    print(vehicle)
    """
    if status not in ["CONNECTADO", "DESCONECTADO"]:
        raise HTTPException(status_code=400,
                            detail="Status inválido. O status deve ser 'CONNECTADO' ou 'DESCONECTADO'.")
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    veiculo.status = status
    db.commit()
    db.refresh(veiculo)
    return veiculo


@app.delete("/veiculos/{veiculo_id}", summary="Exclusão de veículo",
            description="Remove um veículo do sistema pelo ID.")
def excluir_veiculo(veiculo_id: int, db: Session = Depends(get_db),
                    current_user: schemas.Usuario = Depends(get_current_active_user)):
    """
    **Descrição:**
    Remove um veículo do sistema pelo ID.

    **Parâmetros:**
    - `veiculo_id`: ID do veículo (int).

    **Resposta:**
    - 200 OK com uma mensagem de sucesso.
    - 404 Not Found se o veículo não for encontrado.

    **Exemplo de Request:**

    ```http
    DELETE /veiculos/1 HTTP/1.1
    ```

    **Exemplo de Resposta:**

    ```json
    {
        "message": "Veículo excluído com sucesso"
    }
    ```

    **Exemplo de Implementação em Python:**

    ```python
    import httpx

    async def delete_vehicle(token: str, veiculo_id: int):
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"http://127.0.0.1:8000/veiculos/{veiculo_id}", headers={"Authorization": f"Bearer {token}"})
            return response.json()

    # Exemplo de uso
    import asyncio
    result = asyncio.run(delete_vehicle("your_access_token", 1))
    print(result)
    """
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    db.delete(veiculo)
    db.commit()
    return {"message": "Veículo excluído com sucesso"}

