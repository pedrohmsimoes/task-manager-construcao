from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
import config
import os
from werkzeug.utils import secure_filename
import mysql


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Função para abrir conexão
def get_db_connection():
    return mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB,
        port=config.MYSQL_PORT
    )

@app.route('/ping', methods=['GET'])
def ping():
    try:
        db = get_db_connection()
        status = db.is_connected()
        db.close()
        return jsonify({'db_connected': status}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/obras', methods=['GET'])
def get_obras():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM obras")
        obras = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(obras), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/obras/<int:id>', methods=['GET'])
def get_obra_by_id(id):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM obras WHERE id = %s", (id,))
        obra = cursor.fetchone()

        if not obra:
            cursor.close()
            db.close()
            return jsonify({"erro": "Obra não encontrada"}), 404

        cursor.execute("SELECT SUM(custo * quantidade) as total_gasto FROM materiais WHERE obra_id = %s", (id,))
        resultado = cursor.fetchone()
        total_gasto = resultado['total_gasto'] or 0

        obra['total_gasto'] = float(total_gasto)

        orcamento_total = obra.get('orcamento_total') or 0
        percentual_gasto = (total_gasto / orcamento_total) * 100 if orcamento_total > 0 else 0

        obra['percentual_gasto'] = round(percentual_gasto, 1)
        cursor.close()
        db.close()
        # Antes de fechar o cursor:
        obra['cliente_nome'] = obra['cliente_nome'] or "Não informado"
        obra['titulo'] = obra['titulo'] or "Não informado"
        obra['status'] = obra['status'] or "Não informado"
        obra['data_inicio'] = obra['data_inicio'] or "Não informado"
        obra['orcamento_total'] = float(obra['orcamento_total'] or 0)

        return jsonify(obra), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/obras', methods=['POST'])
def create_obra():
    data = request.get_json()
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO obras (cliente_nome, titulo, status, data_inicio, orcamento_total, prazo_entrega)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            str(data.get('cliente_nome')),
            str(data.get('titulo')),
            str(data.get('status')),
            str(data.get('data_inicio')),
            float(data.get('orcamento_total') or 0),
            str(data.get('prazo_entrega'))  # aqui força como string
        ))

        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()
        return jsonify({'msg': 'Obra criada!', 'id': new_id}), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/obras/<int:id>', methods=['PUT'])
def atualizar_obra(id):
    data = request.get_json()
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE obras SET cliente_nome=%s, titulo=%s, status=%s, data_inicio=%s, orcamento_total=%s
            WHERE id=%s
        """, (
            data.get('cliente_nome'),
            data.get('titulo'),
            data.get('status'),
            data.get('data_inicio'),
            data.get('orcamento_total'),
            id
        ))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'msg': 'Obra atualizada com sucesso!'}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/obras/<int:id>', methods=['DELETE'])
def delete_obra(id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM materiais WHERE obra_id = %s", (id,))
        cursor.execute("DELETE FROM obras WHERE id = %s", (id,))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'msg': 'Obra excluída com sucesso!'}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/obras/<int:id>/fotos', methods=['POST'])
def upload_fotos(id):
    try:
        if 'fotos' not in request.files:
            return jsonify({'erro': 'Nenhuma foto enviada'}), 400

        fotos = request.files.getlist('fotos')
        salvas = []

        for foto in fotos:
            filename = secure_filename(foto.filename)
            caminho = os.path.join(UPLOAD_FOLDER, f"obra_{id}_{filename}")
            foto.save(caminho)
            salvas.append(caminho)

        return jsonify({'msg': f'{len(salvas)} fotos salvas com sucesso!'}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/obras/<int:id>/fotos', methods=['GET'])
def listar_fotos(id):
    try:
        fotos = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(f'obra_{id}_')]
        urls = [f'/uploads/{foto}' for foto in fotos]
        return jsonify({'fotos': urls}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/obras/<int:id>/fotos/<nome_arquivo>', methods=['DELETE'])
def excluir_foto(id, nome_arquivo):
    try:
        caminho = os.path.join(UPLOAD_FOLDER, f"obra_{id}_{nome_arquivo}")
        if os.path.exists(caminho):
            os.remove(caminho)
            return jsonify({'msg': 'Foto excluída com sucesso'}), 200
        else:
            return jsonify({'erro': 'Arquivo não encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/obras/<int:obra_id>/materiais', methods=['GET'])
def listar_materiais(obra_id):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM materiais WHERE obra_id = %s", (obra_id,))
        materiais = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(materiais), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/obras/<int:obra_id>/materiais', methods=['POST'])
def adicionar_material(obra_id):
    data = request.get_json()
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO materiais (obra_id, nome, quantidade, custo)
            VALUES (%s, %s, %s, %s)
        """, (
            obra_id,
            data.get('nome'),
            data.get('quantidade'),
            data.get('custo')
        ))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'msg': 'Material adicionado com sucesso!'}), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/materiais/<int:id>', methods=['PUT'])
def atualizar_material(id):
    data = request.get_json()
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE materiais SET nome=%s, quantidade=%s, custo=%s
            WHERE id=%s
        """, (
            data.get('nome'),
            data.get('quantidade'),
            data.get('custo'),
            id
        ))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'msg': 'Material atualizado com sucesso!'}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/materiais/<int:id>', methods=['DELETE'])
def deletar_material(id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM materiais WHERE id = %s", (id,))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'msg': 'Material excluído com sucesso!'}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/obras/<int:obra_id>/gasto-total', methods=['GET'])
def gasto_total_obra(obra_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT SUM(custo * quantidade) FROM materiais WHERE obra_id = %s", (obra_id,))
        total = cursor.fetchone()[0] or 0
        cursor.close()
        db.close()
        return jsonify({'total_gasto': total}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/login', methods=['POST'])
def login_admin():
    data = request.get_json()
    usuario = data.get('usuario')
    senha = data.get('senha')

    # Usuário e senha fixos por enquanto
    if usuario == 'admin' and senha == '1234':
        return jsonify({'sucesso': True, 'msg': 'Login realizado com sucesso!'}), 200
    else:
        return jsonify({'sucesso': False, 'msg': 'Usuário ou senha inválidos.'}), 401

@app.route('/obras/<int:id>/status', methods=['PUT'])
def atualizar_status(id):
    try:
        dados = request.get_json()
        novo_status = dados.get('status')

        print('🔧 Status recebido do front:', novo_status)

        if not novo_status:
            return jsonify({'erro': 'Status não informado'}), 400

        db = get_db_connection()  # pega conexão manual
        cursor = db.cursor()
        cursor.execute("UPDATE obras SET status = %s WHERE id = %s", (novo_status, id))
        db.commit()
        cursor.close()
        db.close()

        return jsonify({'sucesso': True})
    except Exception as e:
        print('❌ Erro ao atualizar status:', e)
        return jsonify({'erro': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
