def listar_obras(mysql):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM obras")
        resultado = cursor.fetchall()
        return resultado
    except Exception as e:
        return {"erro": str(e)}
