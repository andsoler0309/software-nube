import hashlib
from flask_restful import Resource
from flask import request
from models import db, User, UserSchema


class ViewSignInUser(Resource):
    def post(self):
        user = User.query.filter(
            User.username == request.json["username"]
        ).first()

        if user is not None:
            return {"mensaje": "usuario ya existe", 'status': 400}

        if request.json["password1"] != request.json["password2"]:
            return {"mensaje": "password no coinciden", 'status': 400}

        encrypted_password = hashlib.md5(
            request.json["password1"].encode("utf-8")
        ).hexdigest()

        new_user = User(
            username=request.json["username"],
            email=request.json["email"],
            password=encrypted_password
        )
        db.session.add(new_user)
        db.session.commit()

        return {"message": "usuario creado exitosamente", 'status': 200}


class ViewLogin(Resource):
    def post(self):
        encrypted_password = hashlib.md5(
            request.json["password"].encode("utf-8")
        ).hexdigest()
        user = User.query.filter(
            User.username == request.json["username"],
            User.password == encrypted_password,
        ).first()

        if user is None:
            return "El usuario no existe", 404

        return {
            "message": "Inicio de sesión exitoso",
            "id": user.id,
        }, 200
