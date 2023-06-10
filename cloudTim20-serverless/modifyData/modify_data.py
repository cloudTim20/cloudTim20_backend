from utility.upload import *
from utility.Validation import *
from flask import jsonify, g
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta
import json
import jwt



def modify_data(event, context):

    user = g.current_user

    try:
        data = get_from_s3_bucket('user-' + user)
        return data

    except Exception as e:
        return jsonify({'message': 'Error occurred while getting data.', 'error': str(e)}), 500
