from utility.upload import *
from utility.Validation import *
from flask import jsonify, g
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta
import json
import jwt


def update_metadata(event, context):

    user = g.current_user
    json_data = json.load(event['body'])
    file_name = json_data['file_name']
    attribute = json_data['attribute']
    value = json_data['value']

    try:
        update_item_attribute('user-' + user, file_name, attribute, value)
        return jsonify({'message': "File's metadata updated successfully!"})
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return jsonify({'message': 'AWS error', 'error_code': error_code, 'error_message': error_message}), 500
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
