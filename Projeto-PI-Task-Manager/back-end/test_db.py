import mysql.connector, config

try:
    conn = mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB,
        port=config.MYSQL_PORT
    )
    print("Conectado?", conn.is_connected())
    conn.close()
except Exception as e:
    print("Erro ao conectar:", e)
