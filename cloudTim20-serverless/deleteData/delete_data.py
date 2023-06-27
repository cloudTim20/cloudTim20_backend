from utility.upload import *
from utility.Validation import *
from flask import jsonify, g
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta
import json
import jwt


def delete_data(event, context):

    user = g.current_user
    json_data = json.load(event['body'])
    file = json_data['file']

    try:
        delete_file("user-" + user, file)
        return jsonify({'message': 'File deleted successfully!'})
    except FileNotFoundError as e:
        return jsonify({'message': 'File not found.', 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'message': 'Error occurred while deleting file.', 'error': str(e)}), 500
