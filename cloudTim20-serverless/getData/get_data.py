from utility.upload import *
from utility.Validation import *
from flask import jsonify, g
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta
import json
import jwt


def get_data(event, context):

    user = g.current_user

    try:
        # data_s3 = get_from_s3_bucket('user-' + user)
        data_dynamodb = get_from_dynamodb_table('user-' + user)
        return data_dynamodb

    except Exception as e:
        return jsonify({'message': 'Error occurred while getting data.', 'error': str(e)}), 500



