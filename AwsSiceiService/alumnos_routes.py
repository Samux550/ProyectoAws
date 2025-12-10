from flask import Blueprint, request, jsonify, current_app
from models import db, Alumno
import os
import secrets
import time
from aws_helpers import boto3_client, boto3_resource

bp = Blueprint("alumnos", __name__)

def validar_alumno_post(data):
    if "id" in data:
        return jsonify({"error": "No se permite enviar el campo id al crear alumno"}), 400
    required = ["nombres", "apellidos", "matricula", "promedio", "password"]
    for c in required:
        if c not in data or data[c] is None or (isinstance(data[c], str) and data[c].strip() == ""):
            return jsonify({"error": f"El campo '{c}' es obligatorio"}), 400
    if not isinstance(data["nombres"], str) or not isinstance(data["apellidos"], str) or not isinstance(data["matricula"], str):
        return jsonify({"error": "Los campos 'nombres', 'apellidos' y 'matricula' deben ser texto"}), 400
    if not isinstance(data["promedio"], (int, float)):
        return jsonify({"error": "El campo 'promedio' debe ser numérico"}), 400
    if float(data["promedio"]) < 0:
        return jsonify({"error": "El campo 'promedio' debe ser positivo"}), 400
    if not isinstance(data["password"], str) or data["password"].strip() == "":
        return jsonify({"error": "El campo 'password' es obligatorio"}), 400
    return None

def validar_alumno_put(data):
    required = ["nombres", "apellidos", "matricula", "promedio", "password"]
    for c in required:
        if c not in data or data[c] is None or (isinstance(data[c], str) and data[c].strip() == ""):
            return jsonify({"error": f"El campo '{c}' es obligatorio"}), 400
    if not isinstance(data["nombres"], str) or not isinstance(data["apellidos"], str) or not isinstance(data["matricula"], str):
        return jsonify({"error": "Los campos 'nombres', 'apellidos' y 'matricula' deben ser texto"}), 400
    if not isinstance(data["promedio"], (int, float)):
        return jsonify({"error": "El campo 'promedio' debe ser numérico"}), 400
    if float(data["promedio"]) < 0:
        return jsonify({"error": "El campo 'promedio' debe ser positivo"}), 400
    return None

@bp.route("/alumnos", methods=["GET"])
def list_alumnos():
    al = Alumno.query.all()
    return jsonify([a.to_dict() for a in al]), 200

@bp.route("/alumnos", methods=["POST"])
def create_alumno():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío o formato inválido"}), 400
    err = validar_alumno_post(data)
    if err:
        return err
    nuevo = Alumno(
        nombres=data["nombres"].strip(),
        apellidos=data["apellidos"].strip(),
        matricula=data["matricula"].strip(),
        promedio=float(data["promedio"])
    )
    nuevo.set_password(data["password"])
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"id": nuevo.id, "nombres": nuevo.nombres, "apellidos": nuevo.apellidos,
                    "matricula": nuevo.matricula, "promedio": float(nuevo.promedio)}), 201

@bp.route("/alumnos/<int:alumno_id>", methods=["GET"])
def get_alumno(alumno_id):
    a = Alumno.query.get(alumno_id)
    if not a:
        return jsonify({"error": "Alumno no encontrado"}), 404
    return jsonify(a.to_dict()), 200

@bp.route("/alumnos/<int:alumno_id>", methods=["PUT"])
def update_alumno(alumno_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud vacío o no es JSON"}), 400
    err = validar_alumno_put(data)
    if err:
        return err
    a = Alumno.query.get(alumno_id)
    if not a:
        return jsonify({"error": "Alumno no encontrado"}), 404
    a.nombres = data["nombres"].strip()
    a.apellidos = data["apellidos"].strip()
    a.matricula = data["matricula"].strip()
    a.promedio = float(data["promedio"])
    a.set_password(data["password"])
    db.session.commit()
    return jsonify(a.to_dict()), 200

@bp.route("/alumnos/<int:alumno_id>", methods=["DELETE"])
def delete_alumno(alumno_id):
    a = Alumno.query.get(alumno_id)
    if not a:
        return jsonify({"error": "Alumno no encontrado"}), 404
    db.session.delete(a)
    db.session.commit()
    return jsonify({"mensaje": f"Alumno con id {alumno_id} eliminado correctamente"}), 200

@bp.route("/alumnos/<int:alumno_id>/email", methods=["POST"])
def send_email(alumno_id):
    a = Alumno.query.get(alumno_id)
    if not a:
        return jsonify({"error": "Alumno no encontrado"}), 404
    topic_arn = current_app.config.get("SNS_TOPIC_ARN")
    try:
        if topic_arn:
            sns = boto3_client("sns", current_app.config.get("AWS_REGION"))
            sns.publish(TopicArn=topic_arn,
                        Message=f"Alumno: {a.nombres} {a.apellidos}\nMatricula: {a.matricula}\nPromedio: {a.promedio}",
                        Subject=f"Calificaciones {a.nombres} {a.apellidos}")
        return jsonify({"detail": "Mensaje enviado (si SNS configurado)"}), 200
    except Exception as e:
        return jsonify({"error": "Error enviando SNS", "detail": str(e)}), 500

@bp.route("/alumnos/<int:alumno_id>/fotoPerfil", methods=["POST"])
def upload_foto(alumno_id):
    a = Alumno.query.get(alumno_id)
    if not a:
        return jsonify({"error": "Alumno no encontrado"}), 404

    # IMPORTANT: test sends multipart field named "foto"
    if 'foto' not in request.files:
        return jsonify({"error": "No se encontró el archivo (esperado campo 'foto')"}), 400
    file = request.files['foto']
    if file.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    bucket = current_app.config.get("S3_BUCKET")
    if not bucket:
        return jsonify({"error": "S3_BUCKET no configurado"}), 500

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    key = f"alumnos/{alumno_id}/{secrets.token_hex(12)}.{ext}"

    try:
        s3 = boto3_client("s3", current_app.config.get("AWS_REGION"))
        # upload_fileobj with ACL public-read
        s3.upload_fileobj(Fileobj=file, Bucket=bucket, Key=key,
                          ExtraArgs={"ACL": "public-read", "ContentType": file.content_type})
        # Build URL in the exact form required by tests:
        url = f"https://{bucket}.s3.amazonaws.com/{key}"
        a.fotoPerfilUrl = url
        db.session.commit()
        return jsonify({"fotoPerfilUrl": url}), 200
    except Exception as e:
        return jsonify({"error": "Error subiendo a S3", "detail": str(e)}), 500

# ---------------- Sessions (DynamoDB) ----------------
@bp.route("/alumnos/<int:alumno_id>/session/login", methods=["POST"])
def session_login(alumno_id):
    data = request.get_json() or {}
    password = data.get("password")
    if password is None:
        return jsonify({"error": "password requerido"}), 400
    a = Alumno.query.get(alumno_id)
    if not a:
        return jsonify({"error": "Alumno no encontrado"}), 404
    if not a.check_password(password):
        return jsonify({"error": "Credenciales incorrectas"}), 400

    # generate 128-char hex sessionString
    session_string = secrets.token_hex(64)
    fecha = int(time.time())
    item = {
        "sessionString": session_string,
        "fecha": fecha,
        "alumnoId": str(alumno_id),
        "active": True
    }
    try:
        dynamo = boto3_resource("dynamodb", current_app.config.get("AWS_REGION"))
        table_name = current_app.config.get("DYNAMO_TABLE", "sesiones-alumnos")
        table = dynamo.Table(table_name)
        table.put_item(Item=item)
        return jsonify({"sessionString": session_string}), 200
    except Exception as e:
        return jsonify({"error": "Error guardando sesión en DynamoDB", "detail": str(e)}), 500

@bp.route("/alumnos/<int:alumno_id>/session/verify", methods=["POST"])
def session_verify(alumno_id):
    data = request.get_json() or {}
    session_string = data.get("sessionString")
    if session_string is None:
        return jsonify({"error": "sessionString requerido"}), 400
    try:
        dynamo = boto3_resource("dynamodb", current_app.config.get("AWS_REGION"))
        table_name = current_app.config.get("DYNAMO_TABLE", "sesiones-alumnos")
        table = dynamo.Table(table_name)
        resp = table.get_item(Key={"sessionString": session_string})
        item = resp.get("Item")
        if not item:
            return jsonify({"error": "Sesion no encontrada"}), 400
        # check alumnoId matches and active true
        if str(item.get("alumnoId")) != str(alumno_id):
            return jsonify({"error": "Sesion no pertenece al alumno"}), 400
        if item.get("active") is True:
            return jsonify({"detail": "Sesion valida"}), 200
        else:
            return jsonify({"error": "Sesion inactiva"}), 400
    except Exception as e:
        return jsonify({"error": "Error verificando DynamoDB", "detail": str(e)}), 500

@bp.route("/alumnos/<int:alumno_id>/session/logout", methods=["POST"])
def session_logout(alumno_id):
    data = request.get_json() or {}
    session_string = data.get("sessionString")
    if session_string is None:
        return jsonify({"error": "sessionString requerido"}), 400
    try:
        dynamo = boto3_resource("dynamodb", current_app.config.get("AWS_REGION"))
        table_name = current_app.config.get("DYNAMO_TABLE", "sesiones-alumnos")
        table = dynamo.Table(table_name)
        resp = table.get_item(Key={"sessionString": session_string})
        item = resp.get("Item")
        if not item:
            return jsonify({"error": "Sesion no encontrada"}), 400
        if str(item.get("alumnoId")) != str(alumno_id):
            return jsonify({"error": "Sesion no pertenece al alumno"}), 400
        # update active = False
        table.update_item(
            Key={"sessionString": session_string},
            UpdateExpression="SET active = :f",
            ExpressionAttributeValues={":f": False}
        )
        return jsonify({"detail": "Sesion cerrada"}), 200
    except Exception as e:
        return jsonify({"error": "Error actualizando DynamoDB", "detail": str(e)}), 500
