from utility.upload import *
from utility.Validation import *
from flask import jsonify, g
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta
import json
import jwt


def revoke_album_permission(event, context):

    user = g.current_user
    data = json.load(event['body'])
    album = data['album']
    username = data['username']
    table = 'user-' + user

    if (check_string_contains(album, '-') is False) or check_bucket_existence(album) is False:
        return jsonify({'message': 'Album does not exist.'}), 400

    if user == username:
        return jsonify({'message': 'Album for your self is already shared'}), 400

    if not user_exists(username):
        return jsonify({'message': 'Recipient user does not exist.'}), 400

    try:
        remove_album_permission(album, username)
        return jsonify({'message': 'Permission successfully removed from ' + username})
    except Exception as e:
        return jsonify({'message': str(e)}), 400
