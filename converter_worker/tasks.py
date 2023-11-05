import os
from celery.exceptions import Ignore
from utils import get_conversion_command
from celery_worker import celery_app
from celery import states
import db
import time
import tempfile
import subprocess
from google.cloud import storage

GCS_BUCKET_NAME = 'video-converter-1'
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

@celery_app.task(bind=True)
def convert_video(self, input_path, output_path, conversion_type, video_extension, task_id):
    self.update_state(state=states.STARTED, meta={'status': 'Downloading from GCS...'})

    with tempfile.NamedTemporaryFile(suffix=video_extension, delete=False) as input_temp:
        input_temp_filename = input_temp.name

    with tempfile.NamedTemporaryFile(delete=False) as output_temp:
        output_temp_filename = output_temp.name

    try:
        input_blob = bucket.blob(input_path)
        input_blob.download_to_filename(input_temp_filename)

        self.update_state(state=states.STARTED, meta={'status': 'Converting...'})
        cmd = get_conversion_command(input_temp_filename, output_temp_filename, conversion_type)

        with db.session() as session:
            task = session.query(db.VideoConversionTask).filter(
                db.VideoConversionTask.id == task_id
            ).first()
            task.status = db.TaskStatus.STARTED
            task.broker_task_id = self.request.id
            session.commit()

            if cmd:
                time_start = time.time()
                result = subprocess.call(cmd, shell=True)
                time_end = time.time()
                task.time_taken = round(time_end - time_start, 2)

                if result != 0:
                    task.status = db.TaskStatus.FAILURE
                    task.error_message = f'ffmpeg command failed with exit code {result}'
                    session.commit()
                    raise Exception(f"ffmpeg command failed with exit code {result}")

                output_blob = bucket.blob(output_path)
                output_blob.upload_from_filename(output_temp_filename + '.' + conversion_type)

                self.update_state(state=states.SUCCESS, meta={'status': f'File saved to {output_path}'})
                task.status = db.TaskStatus.SUCCESS
                session.commit()

                return f"File converted and saved to {output_path}"
            else:
                task.status = db.TaskStatus.FAILURE
                task.error_message = 'Invalid conversion type'
                session.commit()
                raise Ignore()
    finally:
        os.remove(input_temp_filename)
        os.remove(output_temp_filename)