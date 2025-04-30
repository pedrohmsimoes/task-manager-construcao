from flask import Blueprint, jsonify, request

obra_bp = Blueprint('obra', __name__)

@obra_bp.route('/obras', methods=['GET'])
def get_obras():
    # traz a instância apenas quando a rota é chamada
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM obras")
        obras = cur.fetchall()
        cur.close()
        return jsonify(obras), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@obra_bp.route('/obras', methods=['POST'])
def create_obra():
    from app import mysql

    try:
        data    = request.get_json()
        cliente = data.get('cliente_nome')
        titulo  = data.get('titulo')
        status  = data.get('status')
        inicio  = data.get('data_inicio')

        cur = mysql.connection.cursor()
        cur.execute(
            """
            INSERT INTO obras 
              (cliente_nome, titulo, status, data_inicio) 
            VALUES (%s, %s, %s, %s)
            """,
            (cliente, titulo, status, inicio)
        )
        mysql.connection.commit()
        new_id = cur.lastrowid
        cur.close()

        return jsonify({"msg": "Obra criada!", "id": new_id}), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
