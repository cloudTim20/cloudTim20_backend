from utility.upload import *
from utility.Validation import *
from flask import jsonify, g
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta
import json
import jwt



def revoke_content_permission(event, context):

    user = g.current_user
    data = json.load(event['body'])
    content_key = data['content']
    username = data['username']
    table = 'user-' + user

    if user == username:
        return jsonify({'message': 'Content for your self is already shared'}), 400

    if not user_exists(username):
        return jsonify({'message': 'Recipient user does not exist.'}), 400

    content = get_content_from_database(table, content_key)
    if not content:
        return jsonify({'message': 'Content not found.'}), 404

    try:
        remove_content_permission(table, content_key, username)
        return jsonify({'message': 'Permission successfully removed from ' + username})
    except Exception as e:
        return jsonify({'message': str(e)}), 400
