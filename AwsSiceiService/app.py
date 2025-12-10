from flask import Flask, jsonify
from config import Config
from models import db
from alumnos_routes import bp as alumnos_bp
from profesores_routes import bp as profesores_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # register blueprints
    app.register_blueprint(alumnos_bp)
    app.register_blueprint(profesores_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 5000)))
