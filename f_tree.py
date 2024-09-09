import os


def list_directories_and_files(path, prefix=""):
    # Lista o conteúdo do diretório atual
    items = os.listdir(path)
    items.sort()

    # Itera sobre os itens do diretório
    for i, item in enumerate(items):
        # Caminho completo do item
        full_path = os.path.join(path, item)
        # Verifica se é o último item para ajustar o prefixo
        connector = "└── " if i == len(items) - 1 else "├── "
        # Exibe o item atual
        print(prefix + connector + item)

        # Se for um diretório, chama recursivamente
        if os.path.isdir(full_path):
            # Adiciona um espaçamento para o prefixo
            extension = "    " if i == len(items) - 1 else "│   "
            list_directories_and_files(full_path, prefix + extension)


# Caminho do diretório onde o script está localizado
script_directory = os.path.dirname(os.path.abspath(__file__))
list_directories_and_files(script_directory)
