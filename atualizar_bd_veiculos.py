import sqlite3

# Conecte-se ao banco de dados SQLite
conn = sqlite3.connect('veiculos.db')
cursor = conn.cursor()

# Execute comandos SQL
cursor.execute("PRAGMA table_info(veiculos);")
columns = cursor.fetchall()
print("Colunas atuais:", columns)

conn.close()