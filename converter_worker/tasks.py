import os
import json
from utils import get_conversion_command
import db
import time
import tempfile
import subprocess
from google.cloud import storage, pubsub_v1

GCS_BUCKET_NAME = 'video-converter-1'
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)


def convert_video(data):
    input_path = data['input_path']
    output_path = data['output_path']
    conversion_type = data['conversion_type']
    file_extension = data['file_extension']
    task_id = data['task_id']

    with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as input_temp:
        input_temp_filename = input_temp.name

    with tempfile.NamedTemporaryFile(delete=False) as output_temp:
        output_temp_filename = output_temp.name

    try:
        input_blob = bucket.blob(input_path)
        input_blob.download_to_filename(input_temp_filename)

        cmd = get_conversion_command(input_temp_filename, output_temp_filename, conversion_type)

        with db.session() as session:
            task = session.query(db.VideoConversionTask).filter(
                db.VideoConversionTask.id == task_id
            ).first()
            task.status = db.TaskStatus.STARTED
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
                    return {'error': f"ffmpeg command failed with exit code {result}"}

                output_blob = bucket.blob(output_path)
                output_blob.upload_from_filename(output_temp_filename + '.' + conversion_type)

                task.status = db.TaskStatus.SUCCESS
                session.commit()
                return {'success': f"File converted and saved to {output_path}"}
            else:
                task.status = db.TaskStatus.FAILURE
                task.error_message = 'Invalid conversion type'
                session.commit()
                return {'error': 'Invalid conversion type'}
    finally:
        os.remove(input_temp_filename)
        os.remove(output_temp_filename)

def callback(message):
    data = json.loads(message.data.decode('utf-8'))
    result = convert_video(data)
    if result.get('error'):
        message.nack()
    else:
        message.ack()

def main():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path('video-convertor-402921', 'video-sub')
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    with subscriber:
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            streaming_pull_future.result()

if __name__ == '__main__':
    main()