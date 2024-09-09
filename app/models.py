# app/models.py

from sqlalchemy import Column, Integer, String
from .database import Base

class Veiculo(Base):
    __tablename__ = "veiculos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    modelo = Column(String, index=True)
    status = Column(String, default="DESCONECTADO")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)