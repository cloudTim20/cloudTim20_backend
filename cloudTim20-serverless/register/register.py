from utility.upload import *
from utility.Validation import *
from flask import jsonify
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta
import json
import jwt

def register(event, context):
    user = json.loads(event['body'])

    # Lepimo podatke iz Json requesta
    name = user['name']
    surname = user['surname']
    username = user['username']
    birth_date = user['birth_date']
    email = user['email']
    password = user['password']

    # Validacija
    if not validate_datetime(birth_date):
        return jsonify({'message': 'Invalid datetime format for birth_date.'}), 400

    if not validate_email(email):
        return jsonify({'message': 'Invalid email format.'}), 400

    if not validate_length(name, 2, 50):
        return jsonify({'message': 'Invalid name length.'}), 400

    if not validate_length(surname, 2, 50):
        return jsonify({'message': 'Invalid surname length.'}), 400

    if not validate_length(username, 2, 50):
        return jsonify({'message': 'Invalid username length.'}), 400

    if not validate_length(email, 6, 50):
        return jsonify({'message': 'Invalid email length.'}), 400

    if not validate_length(password, 6, 50):
        return jsonify({'message': 'Invalid password length.'}), 400

    if dynamodb_check_if_exists('users', 'username', username):
        return jsonify({'message': 'Username is already taken.'}), 400

    dynamodb_insert_into_table('users', user)

    s3_create_bucket("user-" + username)
    dynamodb_create_table("user-" + username, "file_name")

    return jsonify({'message': 'User registered successfully!'})
