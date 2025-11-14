from flask import Flask,jsonify,request

app = Flask(__name__)

alumnos=[]
contador_alumnos_id = 1
profesores = []
contador_profesor_id = 1

##creacion de endpoints

##GET/alumnos
@app.route('/alumnos',methods=['GET'])
def get_alumnos():
    return alumnos,200

##GET/alumnos/id
@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumnos_by_id(id):
    ##buscar por la id del alumno
    for alumno in alumnos:
        if alumno["id"] == id:
            return jsonify(alumno), 200
    return jsonify({"error": "Alumno no encontrado"}), 404

##POST/alumnos
@app.route('/alumnos', methods=['POST'])
def crear_alumno():
    global contador_alumnos_id
    
    data = request.get_json()

    #Validacion de datos
    error = validar_datos(data)
    if error:
        return error
    # Crear el nuevo alumno
    nuevo_alumno = {
        "id": contador_alumnos_id,
        "nombres": data["nombres"],
        "apellidos": data["apellidos"],
        "matricula": data["matricula"],
        "promedio": data["promedio"]
    }

    # Agregar al arreglo
    alumnos.append(nuevo_alumno)
    contador_alumnos_id += 1

    # Respuesta de éxito
    return jsonify(nuevo_alumno), 201

##PUT/alumnos
@app.route('/alumnos/<int:id>', methods=['PUT'])
def modificar_alumno(id):
    # Obtener JSON del body
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud vacío o no es JSON"}), 400

    # Validar los datos usando la función validar_datos
    resultado_validacion = validar_datos(data)
    if resultado_validacion is not None:
        # validar_datos puede devolver (json_response, status) o directamente (json_response, status)
        # Si tu validar_datos ya devuelve jsonify(...),status entonces lo retornamos tal cual
        return resultado_validacion

    # Buscar el alumno por id y actualizar sus campos
    for alumno in alumnos:
        if alumno["id"] == id:
            # Aquí asumimos que el PUT reemplaza/actualiza todos los campos esperados
            alumno["nombres"] = data["nombres"]
            alumno["apellidos"] = data["apellidos"]
            alumno["matricula"] = data["matricula"]
            alumno["promedio"] = data["promedio"]
            return jsonify(alumno), 200

    # Si no se encontró el alumno
    return jsonify({"error": "Alumno no encontrado"}), 404

#DELETE/alumnos
@app.route('/alumnos/<int:id>', methods=['DELETE'])
def eliminar_alumno(id):
    for alumno in alumnos:
        if alumno["id"] == id:
            alumnos.remove(alumno)
            return jsonify({"mensaje": f"Alumno con id {id} eliminado correctamente"}), 200

    return jsonify({"error": "Alumno no encontrado"}), 404

def validar_datos(data):
    
    # Validar que todos los campos existan
    campos_requeridos = ["nombres", "apellidos", "matricula", "promedio"]
    for campo in campos_requeridos:
        if campo not in data or data[campo] == "":
            return jsonify({"error": f"El campo '{campo}' es obligatorio"}), 400

    # Validar tipos básicos
    if not isinstance(data["nombres"], str) or not isinstance(data["apellidos"], str) or not isinstance(data["matricula"], str):
        return jsonify({"error": "Los campos 'nombres', 'apellidos' y 'matricula' deben ser texto"}), 400

    if not isinstance(data["promedio"], (int, float)):
        return jsonify({"error": "El campo 'promedio' debe ser numérico"}), 400
    
    return None

# GET /profesores
@app.route('/profesores', methods=['GET'])
def get_profesores():
    return jsonify(profesores), 200


# GET /profesores/<id>
@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor_by_id(id):
    for profesor in profesores:
        if profesor["id"] == id:
            return jsonify(profesor), 200
    return jsonify({"error": "Profesor no encontrado"}), 404


# POST /profesores
@app.route('/profesores', methods=['POST'])
def crear_profesor():
    global contador_profesor_id

    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío o formato inválido"}), 400

    # Validar datos
    error = validar_datos_profesor(data)
    if error:
        return error

    # Crear el nuevo profesor
    nuevo_profesor = {
        "id": contador_profesor_id,
        "numeroEmpleado": data["numeroEmpleado"],
        "nombres": data["nombres"],
        "apellidos": data["apellidos"],
        "horasClase": data["horasClase"]
    }

    profesores.append(nuevo_profesor)
    contador_profesor_id += 1

    return jsonify(nuevo_profesor), 201


# PUT /profesores/<id>
@app.route('/profesores/<int:id>', methods=['PUT'])
def modificar_profesor(id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud vacío o no es JSON"}), 400

    # Validar los datos
    resultado_validacion = validar_datos_profesor(data)
    if resultado_validacion is not None:
        return resultado_validacion

    # Buscar y actualizar profesor
    for profesor in profesores:
        if profesor["id"] == id:
            profesor["numeroEmpleado"] = data["numeroEmpleado"]
            profesor["nombres"] = data["nombres"]
            profesor["apellidos"] = data["apellidos"]
            profesor["horasClase"] = data["horasClase"]
            return jsonify(profesor), 200

    return jsonify({"error": "Profesor no encontrado"}), 404


# DELETE /profesores/<id>
@app.route('/profesores/<int:id>', methods=['DELETE'])
def eliminar_profesor(id):
    for profesor in profesores:
        if profesor["id"] == id:
            profesores.remove(profesor)
            return jsonify({"mensaje": f"Profesor con id {id} eliminado correctamente"}), 200

    return jsonify({"error": "Profesor no encontrado"}), 404


# Validación para profesores
def validar_datos_profesor(data):

    campos_requeridos = ["numeroEmpleado", "nombres", "apellidos", "horasClase"]

    for campo in campos_requeridos:
        if campo not in data or data[campo] == "" or data[campo] is None:
            return jsonify({"error": f"El campo '{campo}' es obligatorio"}), 400

    if not isinstance(data["numeroEmpleado"], str):
        return jsonify({"error": "El campo 'numeroEmpleado' debe ser texto"}), 400

    if not isinstance(data["nombres"], str) or not isinstance(data["apellidos"], str):
        return jsonify({"error": "Los campos 'nombres' y 'apellidos' deben ser texto"}), 400

    if not isinstance(data["horasClase"], int) or data["horasClase"] < 0:
        return jsonify({"error": "El campo 'horasClase' debe ser un número entero positivo"}), 400

    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
