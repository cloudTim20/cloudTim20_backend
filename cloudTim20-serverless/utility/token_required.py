from Flask import request, jsonify, g
from functools import wraps
from jwt.exceptions import DecodeError
import jwt
#TODO drugciji dekorator za header-e iz event argumenta
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
            g.current_user = data['username']
        except DecodeError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated_function