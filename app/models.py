# app/models.py

from sqlalchemy import Column, Integer, String, CheckConstraint
from .database import Base

class Veiculo(Base):
    __tablename__ = "veiculos"

    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String, index=True)
    modelo = Column(String, index=True)
    ano = Column(Integer)  # Adicionado o campo 'ano'
    placa = Column(String, unique=True, index=True)  # Placa deve ser única
    status = Column(String, default="DESCONECTADO")

    __table_args__ = (
        CheckConstraint(
            "status IN ('CONNECTADO', 'DESCONECTADO')",
            name="check_status"
        ),
    )

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
