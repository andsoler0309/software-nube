import hashlib
import os
import datetime
from flask_restful import Resource
from flask import request, abort, current_app, send_from_directory
from models import db, User, UserSchema, VideoConversionTask, VideoConversionTaskSchema, TaskStatus
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from extensions import celery
from werkzeug.utils import secure_filename
from google.cloud import storage, pubsub_v1
import json

tasks_schema = VideoConversionTaskSchema(many=True)
task_schema = VideoConversionTaskSchema()

# cloud storage config
GCS_BUCKET_NAME = 'video-converter-1'
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

# pubsub config
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('video-convertor-402921', 'convert-video')


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

        return {"message": "usuario creado exitosamente", "id": new_user.id}, 201


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

        access_token = create_access_token(identity=user.id)
        return {
            "message": "Inicio de sesión exitoso",
            "token": access_token,
            "id": user.id,
        }, 200


class ViewConverter(Resource):
    @jwt_required()
    def post(self):
        if 'file' not in request.files:
            return {'error': 'No file part'}, 400

        file = request.files['file']
        if file.filename == '' or not file:
            return {'error': 'No selected file'}, 400

        filename = secure_filename(file.filename)
        file_basename, file_extension = os.path.splitext(filename)

        user_id_str = str(get_jwt_identity())
        conversion_type = request.form.get('conversion_type')
        gcs_upload_path = f'uploads/{user_id_str}/{filename}'
        gcs_output_path = f'converted/{user_id_str}/converted_{file_basename}.{conversion_type}'

        upload_blob = bucket.blob(gcs_upload_path)
        upload_blob.upload_from_string(file.read(), content_type=file.content_type)

        input_path = gcs_upload_path
        output_path = gcs_output_path

        task_entry = VideoConversionTask(
            user_id=get_jwt_identity(),
            input_path=input_path,
            output_path=output_path,
            conversion_type=conversion_type,
            status=TaskStatus.PENDING
        )
        db.session.add(task_entry)
        db.session.commit()
        task_id = task_entry.id

        try:
            data = json.dumps({
                'input_path': input_path,
                'output_path': output_path,
                'conversion_type': conversion_type,
                'file_extension': file_extension,
                'task_id': task_id
            }).encode('utf-8')
            future = publisher.publish(topic_path, data=data)
            future.result()
            return {"message": "Conversion started", "task_id": str(task_id)}, 202
        except Exception as e:
            task_entry.status = TaskStatus.FAILURE
            task_entry.error_message = str(e)
            db.session.commit()
            return {"error": str(e)}, 500

    @jwt_required()
    def get(self):
        order = request.args.get('order')
        max_results = request.args.get('max')
        user_id = get_jwt_identity()

        tasks_query = VideoConversionTask.query.filter_by(user_id=user_id)

        if order == '1':
            tasks_query = tasks_query.order_by(VideoConversionTask.id.desc())
        else:
            tasks_query = tasks_query.order_by(VideoConversionTask.id.asc())

        if max_results:
            tasks_query = tasks_query.limit(int(max_results))

        tasks = tasks_query.all()
        return {"tasks": tasks_schema.dump(tasks)}, 200


class ViewConverterStatus(Resource):
    @jwt_required()
    def get(self, task_id):
        task = VideoConversionTask.query.filter_by(id=task_id).first()
        if not task:
            return {"error": "Task not found"}, 404

        if task.user_id != get_jwt_identity():
            return {"error": "Not authorized to view this task"}, 403

        return {"task": task_schema.dump(task)}, 200

    @jwt_required()
    def delete(self, task_id):
        try:
            task = VideoConversionTask.query.filter_by(id=task_id).first()
            if not task:
                return {"error": "Task not found"}, 404

            if task.user_id != get_jwt_identity():
                return {"error": "Not authorized to delete this task"}, 403

            bucket.blob(task.input_path).delete()
            bucket.blob(task.output_path).delete()
            db.session.delete(task)
            db.session.commit()
            return {}, 204

        except Exception as e:
            return {"error": str(e)}, 500


class ViewFileDownload(Resource):
    @jwt_required()
    def get(self):
        task_id = request.args.get('task_id')
        if not task_id:
            return {'error': 'Task id is required'}, 400

        try:
            task = VideoConversionTask.query.filter_by(id=task_id).first()
            if not task:
                return {"error": "Task not found"}, 404

            if task.user_id != get_jwt_identity():
                return {"error": "Not authorized to download this file"}, 403

            if task.status != TaskStatus.SUCCESS:
                return {"error": "File is not ready for download"}, 400

            blob_name = task.output_path
            blob = bucket.blob(blob_name)
            blob_uri = blob.generate_signed_url(
                version='v4',
                expiration=datetime.timedelta(minutes=5), # 5 minutes
                method='GET'
            )
            return {'download_url': blob_uri}
            # filepath = task.output_path + '.' + task.conversion_type
            # directory, filename = os.path.split(filepath)
            # return send_from_directory(directory, filename, as_attachment=True)
        except google.cloud.exceptions.NotFound:
            return {'error': 'file not found'}, 404
        except Exception as e:
            return {"error": str(e)}, 500
