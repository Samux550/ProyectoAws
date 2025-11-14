from flask import Flask, jsonify, request

app = Flask(__name__)

alumnos = []
profesores = []


# =====================================================
# ALUMNOS
# =====================================================

@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    return jsonify(alumnos), 200


@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumnos_by_id(id):
    for alumno in alumnos:
        if alumno["id"] == id:
            return jsonify(alumno), 200
    return jsonify({"error": "Alumno no encontrado"}), 404


@app.route('/alumnos', methods=['POST'])
def crear_alumno():

    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío o formato inválido"}), 400

    error = validar_datos_alumno(data)
    if error:
        return error

    nuevo_alumno = {
        "id": data["id"],
        "nombres": data["nombres"],
        "apellidos": data["apellidos"],
        "matricula": data["matricula"],
        "promedio": data["promedio"]
    }

    alumnos.append(nuevo_alumno)

    return jsonify(nuevo_alumno), 201


@app.route('/alumnos/<int:id>', methods=['PUT'])
def modificar_alumno(id):

    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud vacío o no es JSON"}), 400

    error = validar_datos_alumno(data)
    if error:
        return error

    for alumno in alumnos:
        if alumno["id"] == id:
            alumno["nombres"] = data["nombres"]
            alumno["apellidos"] = data["apellidos"]
            alumno["matricula"] = data["matricula"]
            alumno["promedio"] = data["promedio"]
            return jsonify(alumno), 200

    return jsonify({"error": "Alumno no encontrado"}), 404


@app.route('/alumnos/<int:id>', methods=['DELETE'])
def eliminar_alumno(id):
    for alumno in alumnos:
        if alumno["id"] == id:
            alumnos.remove(alumno)
            return jsonify({"mensaje": f"Alumno con id {id} eliminado correctamente"}), 200

    return jsonify({"error": "Alumno no encontrado"}), 404


def validar_datos_alumno(data):

    campos = ["id", "nombres", "apellidos", "matricula", "promedio"]

    for c in campos:
        if c not in data or data[c] is None or data[c] == "":
            return jsonify({"error": f"El campo '{c}' es obligatorio"}), 400

    if not isinstance(data["id"], int):
        return jsonify({"error": "El campo 'id' debe ser numérico"}), 400

    if not isinstance(data["nombres"], str) or not isinstance(data["apellidos"], str) or not isinstance(data["matricula"], str):
        return jsonify({"error": "Los campos 'nombres', 'apellidos' y 'matricula' deben ser texto"}), 400

    if not isinstance(data["promedio"], (int, float)):
        return jsonify({"error": "El campo 'promedio' debe ser numérico"}), 400

    if data["promedio"] < 0:
        return jsonify({"error": "El campo 'promedio' debe ser positivo"}), 400

    return None


# =====================================================
# PROFESORES
# =====================================================

@app.route('/profesores', methods=['GET'])
def get_profesores():
    return jsonify(profesores), 200


@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor_by_id(id):
    for profesor in profesores:
        if profesor["id"] == id:
            return jsonify(profesor), 200
    return jsonify({"error": "Profesor no encontrado"}), 404


@app.route('/profesores', methods=['POST'])
def crear_profesor():

    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío o formato inválido"}), 400

    error = validar_datos_profesor(data)
    if error:
        return error

    nuevo_profesor = {
        "id": data["id"],
        "numeroEmpleado": data["numeroEmpleado"],
        "nombres": data["nombres"],
        "apellidos": data["apellidos"],
        "horasClase": data["horasClase"]
    }

    profesores.append(nuevo_profesor)

    return jsonify(nuevo_profesor), 201


@app.route('/profesores/<int:id>', methods=['PUT'])
def modificar_profesor(id):

    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud vacío o no es JSON"}), 400

    error = validar_datos_profesor(data)
    if error:
        return error

    for profesor in profesores:
        if profesor["id"] == id:
            profesor["numeroEmpleado"] = data["numeroEmpleado"]
            profesor["nombres"] = data["nombres"]
            profesor["apellidos"] = data["apellidos"]
            profesor["horasClase"] = data["horasClase"]
            return jsonify(profesor), 200

    return jsonify({"error": "Profesor no encontrado"}), 404


@app.route('/profesores/<int:id>', methods=['DELETE'])
def eliminar_profesor(id):
    for profesor in profesores:
        if profesor["id"] == id:
            profesores.remove(profesor)
            return jsonify({"mensaje": f"Profesor con id {id} eliminado correctamente"}), 200

    return jsonify({"error": "Profesor no encontrado"}), 404


def validar_datos_profesor(data):

    campos = ["id", "numeroEmpleado", "nombres", "apellidos", "horasClase"]

    for c in campos:
        if c not in data or data[c] is None or data[c] == "":
            return jsonify({"error": f"El campo '{c}' es obligatorio"}), 400

    if not isinstance(data["id"], int):
        return jsonify({"error": "El campo 'id' debe ser numérico"}), 400

    # Aceptar numeroEmpleado como texto o número
    if not isinstance(data["numeroEmpleado"], (str, int, float)):
        return jsonify({"error": "El campo 'numeroEmpleado' debe ser texto o numérico"}), 400

    if not isinstance(data["nombres"], str) or not isinstance(data["apellidos"], str):
        return jsonify({"error": "Los campos 'nombres' y 'apellidos' deben ser texto"}), 400

    # Aceptar horasClase como entero o float (test usa double)
    if not isinstance(data["horasClase"], (int, float)):
        return jsonify({"error": "El campo 'horasClase' debe ser numérico"}), 400

    if data["horasClase"] < 0:
        return jsonify({"error": "El campo 'horasClase' debe ser positivo"}), 400

    return None


# =====================================================
# RUN
# =====================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
