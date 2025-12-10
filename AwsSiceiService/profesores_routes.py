from flask import Blueprint, request, jsonify
from models import db, Profesor

bp = Blueprint("profesores", __name__)

def validar_profesor_post(data):
    if "id" in data:
        return jsonify({"error": "No se permite enviar el campo id al crear profesor"}), 400
    campos = ["numeroEmpleado", "nombres", "apellidos", "horasClase"]
    for c in campos:
        if c not in data or data[c] is None or (isinstance(data[c], str) and data[c].strip() == ""):
            return jsonify({"error": f"El campo '{c}' es obligatorio"}), 400
    # numeroEmpleado can be str or numeric
    ne = data["numeroEmpleado"]
    if isinstance(ne, (int, float)) and ne < 0:
        return jsonify({"error": "El campo 'numeroEmpleado' no puede ser negativo"}), 400
    if not isinstance(data["nombres"], str) or not isinstance(data["apellidos"], str):
        return jsonify({"error": "Los campos 'nombres' y 'apellidos' deben ser texto"}), 400
    if not isinstance(data["horasClase"], (int, float)):
        return jsonify({"error": "El campo 'horasClase' debe ser numérico"}), 400
    if float(data["horasClase"]) < 0:
        return jsonify({"error": "El campo 'horasClase' debe ser positivo"}), 400
    return None

def validar_profesor_put(data):
    # same validation as post
    return validar_profesor_post(data)

@bp.route("/profesores", methods=["GET"])
def list_profesores():
    items = Profesor.query.all()
    return jsonify([p.to_dict() for p in items]), 200

@bp.route("/profesores", methods=["POST"])
def create_profesor():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío o formato inválido"}), 400
    err = validar_profesor_post(data)
    if err:
        return err
    nuevo = Profesor(
        numeroEmpleado=str(data["numeroEmpleado"]),
        nombres=data["nombres"].strip(),
        apellidos=data["apellidos"].strip(),
        horasClase=float(data["horasClase"])
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"id": nuevo.id, "numeroEmpleado": nuevo.numeroEmpleado,
                    "nombres": nuevo.nombres, "apellidos": nuevo.apellidos,
                    "horasClase": float(nuevo.horasClase)}), 201

@bp.route("/profesores/<int:profesor_id>", methods=["GET"])
def get_profesor(profesor_id):
    p = Profesor.query.get(profesor_id)
    if not p:
        return jsonify({"error": "Profesor no encontrado"}), 404
    return jsonify(p.to_dict()), 200

@bp.route("/profesores/<int:profesor_id>", methods=["PUT"])
def update_profesor(profesor_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud vacío o no es JSON"}), 400
    err = validar_profesor_put(data)
    if err:
        return err
    p = Profesor.query.get(profesor_id)
    if not p:
        return jsonify({"error": "Profesor no encontrado"}), 404
    p.numeroEmpleado = str(data["numeroEmpleado"])
    p.nombres = data["nombres"].strip()
    p.apellidos = data["apellidos"].strip()
    p.horasClase = float(data["horasClase"])
    db.session.commit()
    return jsonify(p.to_dict()), 200

@bp.route("/profesores/<int:profesor_id>", methods=["DELETE"])
def delete_profesor(profesor_id):
    p = Profesor.query.get(profesor_id)
    if not p:
        return jsonify({"error": "Profesor no encontrado"}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({"mensaje": f"Profesor con id {profesor_id} eliminado correctamente"}), 200
