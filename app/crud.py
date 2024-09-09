# app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funções CRUD para Veículos

def get_veiculo(db: Session, veiculo_id: int):
    return db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()

def get_veiculos(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Veiculo).offset(skip).limit(limit).all()

def create_veiculo(db: Session, veiculo: schemas.VeiculoCreate):
    db_veiculo = models.Veiculo(**veiculo.model_dump())
    db.add(db_veiculo)
    db.commit()
    db.refresh(db_veiculo)
    return db_veiculo

def update_veiculo_status(db: Session, veiculo_id: int, status: str):
    veiculo = get_veiculo(db, veiculo_id)
    if veiculo:
        veiculo.status = status
        db.commit()
        db.refresh(veiculo)
    return veiculo

def delete_veiculo(db: Session, veiculo_id: int):
    veiculo = get_veiculo(db, veiculo_id)
    if veiculo:
        db.delete(veiculo)
        db.commit()
    return veiculo

# Funções CRUD para Usuários

def get_usuario_by_username(db: Session, username: str):
    return db.query(models.Usuario).filter(models.Usuario.username == username).first()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed_password = pwd_context.hash(usuario.password)
    db_usuario = models.Usuario(username=usuario.username, hashed_password=hashed_password)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def delete_usuario(db: Session, usuario_id: int):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario:
        db.delete(usuario)
        db.commit()
    return usuario
