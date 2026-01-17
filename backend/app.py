from __future__ import annotations

import os

from flask import Flask, jsonify
from flask_cors import CORS

from .database import init_db
from .routes.ai_routes import ai_bp
from .routes.auth_routes import auth_bp
from .routes.novel_routes import novel_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(novel_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"code": "OK"})

    return app


if __name__ == "__main__":
    app = create_app()
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=True)

