# app/schemas.py

from pydantic import BaseModel, constr, conint, field_validator

# Esquema para criação de um novo veículo
class VeiculoCreate(BaseModel):
    marca: str
    modelo: str
    ano: conint(ge=1886)  # Ano deve ser um inteiro maior ou igual a 1886 (ano do primeiro carro)
    placa: constr(min_length=7, max_length=7)  # Placa deve ter um comprimento fixo, por exemplo 7 caracteres
    status: str = "DESCONECTADO"  # Valor padrão

    @field_validator('status')
    def status_must_be_valid(cls, v):
        if v not in ["CONNECTADO", "DESCONECTADO"]:
            raise ValueError('Status deve ser "CONNECTADO" ou "DESCONECTADO"')
        return v

# Esquema para o veículo com ID (usado nas respostas)
class Veiculo(BaseModel):
    id: int
    marca: str
    modelo: str
    ano: int
    placa: str
    status: str

    class Config:
        from_attributes = True  # Necessário para compatibilidade com SQLAlchemy

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
