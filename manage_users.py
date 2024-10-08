# manage_users.py

import argparse
from sqlalchemy.orm import Session
from app import crud, database, schemas


def main():
    parser = argparse.ArgumentParser(description="Gerenciar usuários do banco de dados")
    parser.add_argument("action", choices=["create", "list", "delete"], help="Ação a ser realizada")
    parser.add_argument("--username", help="Nome de usuário")
    parser.add_argument("--password", help="Senha do usuário")

    args = parser.parse_args()

    # Usando 'with' para garantir que a sessão será fechada corretamente
    with database.SessionLocal() as db:
        try:
            if args.action == "create":
                if not args.username or not args.password:
                    print("Usuário e senha são necessários para criar um novo usuário.")
                    return

                # Verificando se o usuário já existe
                existing_user = crud.get_usuario_by_username(db, args.username)
                if existing_user:
                    print(f"Usuário '{args.username}' já existe.")
                    return

                # Criando o usuário
                usuario = schemas.UsuarioCreate(username=args.username, password=args.password)
                crud.create_usuario(db, usuario)
                print(f"Usuário '{args.username}' criado com sucesso.")

            elif args.action == "list":
                # Listando todos os usuários
                usuarios = db.query(crud.models.Usuario).all()
                for usuario in usuarios:
                    print(f"ID: {usuario.id}, Username: {usuario.username}")

            elif args.action == "delete":
                if not args.username:
                    print("Nome de usuário é necessário para excluir um usuário.")
                    return

                # Verificando se o usuário existe
                usuario = crud.get_usuario_by_username(db, args.username)
                if usuario:
                    # Excluindo o usuário
                    crud.delete_usuario(db, usuario.id)
                    print(f"Usuário '{args.username}' excluído com sucesso.")
                else:
                    print(f"Usuário '{args.username}' não encontrado.")

        except Exception as e:
            print(f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    main()
