from utility.upload import *
from utility.Validation import *
from flask import jsonify, g
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta
import json
import jwt

def download_file(event, context):

    user = g.current_user
    json_data = json.load(event['body'])
    file_name = json_data['file_name']
    destination_path = json_data['destination_path']

    try:
        s3_download_file('user-' + user, file_name, destination_path)
        return jsonify({'message': 'File downloaded successfully!'})
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return jsonify({'message': 'AWS error', 'error_code': error_code, 'error_message': error_message}), 500
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
