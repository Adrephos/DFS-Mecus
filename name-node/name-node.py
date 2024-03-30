from flask import Flask, request, jsonify
from tinydb import TinyDB, Query

# Inicialización y configuración de Flask
# Server
app = Flask(__name__)


@app.route('/', methods=['POST'])
def recibir_mensaje():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    # PONGAN AQUÍ LA LÓGICA QUE GUARDA ESOS DATOS EN LA BASE DE DATOS :D
    if data:
        respuesta = {"response": "Successful registration"}
    else:
        respuesta = {"response": "Unknown message."}

    return jsonify(respuesta), 200


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
