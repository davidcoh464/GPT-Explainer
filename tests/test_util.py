from flask_imp.db_model import Upload
import os


def clear_resource(upload_uid: str):
    for file in os.listdir('uploads'):
        if file.startswith(upload_uid):
            os.remove(os.path.join('uploads', file))
    for file in os.listdir('outputs'):
        if file.startswith(upload_uid):
            os.remove(os.path.join('outputs', file))
    Upload.delete_by_uid(upload_uid)