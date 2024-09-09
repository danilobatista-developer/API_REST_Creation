# app/schemas.py

from pydantic import BaseModel

# Esquema para criação de um novo veículo
class VeiculoCreate(BaseModel):
    nome: str
    modelo: str
    status: str = "DESCONECTADO"  # Valor padrão

# Esquema para o veículo com ID (usado nas respostas)
class Veiculo(BaseModel):
    id: int
    nome: str
    modelo: str
    status: str

    class Config:
        from_attributes  = True  # Necessário para compatibilidade com SQLAlchemy

# Esquema para autorização de usuários
class UsuarioBase(BaseModel):
    username: str

class UsuarioCreate(UsuarioBase):
    password: str

class Usuario(UsuarioBase):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None