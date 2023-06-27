from utility.upload import *
from utility.Validation import *
from flask import jsonify, g
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta
import json
import jwt

def upload_data(event, context):

    user = g.current_user
    json_data = json.loads(event['body'])

    file_path = json_data['file_path']
    file_name = json_data['file_name']
    description = json_data['description']
    tags = json_data['tags']

    try:
        if not tags:
            upload('user-' + user, file_path, file_name, description)
        else:
            upload(user, file_path, file_name, description, tags)
        return jsonify({'message': 'File uploaded successfully!'})

    except Exception as e:
        return jsonify({'message': 'Error occurred while uploading file.', 'error': str(e)}), 500
