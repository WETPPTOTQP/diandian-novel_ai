from __future__ import annotations

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from ..config import load_config
from ..database import SessionLocal
from ..models import User
from ..utils.security import create_token, hash_password, verify_password


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
config = load_config()


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()
    if not username or not password:
        return jsonify({"code": "INVALID_INPUT", "message": "用户名或密码不能为空"}), 400

    with SessionLocal() as db:
        exists = db.scalar(select(User).where(User.username == username))
        if exists:
            return jsonify({"code": "USERNAME_TAKEN", "message": "用户名已存在"}), 409
        user = User(username=username, password_hash=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_token(config.auth_secret, str(user.id), config.auth_token_ttl_seconds)
    return jsonify({"code": "OK", "data": {"token": token, "user": {"id": user.id, "username": user.username}}})


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()
    if not username or not password:
        return jsonify({"code": "INVALID_INPUT", "message": "用户名或密码不能为空"}), 400

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == username))
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"code": "INVALID_CREDENTIALS", "message": "用户名或密码错误"}), 401

    token = create_token(config.auth_secret, str(user.id), config.auth_token_ttl_seconds)
    return jsonify({"code": "OK", "data": {"token": token, "user": {"id": user.id, "username": user.username}}})
