from utility.upload import *
from utility.Validation import *
from flask import jsonify
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta
import json
import jwt


def login(event, context):
    headers = event['headers']
    auth = headers.get('Authorization')

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Cloud not verify', 'WWW-Authenticate': 'Basic auth="Login required"'}), 401

    if not dynamodb_check_if_exists('users', 'username', auth.username):
        return jsonify({'message': 'User not found', 'data': {}}), 401

    primary_key = {
        'username': {"S": auth.username}
    }
    response = dynamodb_client.get_item(
        TableName='users',
        Key=primary_key
    )

    user = response['Item']

    if user['password']['S'] == auth.password:
        token = jwt.encode({'username': user['username']['S'], 'exp': datetime.utcnow() + timedelta(minutes=30)}) # TODO: app.config['SECRET_KEY'] ??
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials', 'data': {}}), 401
