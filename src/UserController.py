from flask import Flask, jsonify, request
# from User import User
from Validation import validate_email, validate_datetime, validate_length
import jwt
from datetime import datetime, timedelta
from upload import *
from functools import wraps
from jwt.exceptions import DecodeError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
users = []

@app.route('/register', methods=['POST'])
def register():
    user = request.get_json()

    #Lepimo podatke iz Json requesta
    name = user['name']
    surname = user['surname']
    username = user['username']
    birth_date = user['birth_date']
    email = user['email']
    password = user['password']

    #Validacija
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

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return jsonify({'message':'Cloud not vertify', 'WWWWW-Authenricate':'Basic auth="Login required"'}), 401

    # user = next((user for user in users if user.username == auth.username), None)
    
    if not dynamodb_check_if_exists('users', 'username', auth.username):
        return jsonify({'message':'User not found', 'data':{}}), 401

    primary_key = {
        'username': {"S": auth.username}
    }
    response = dynamodb_client.get_item(
        TableName='users',
        Key=primary_key
    )

    user = response['Item']

    if user['password']['S'] == auth.password:
        token = jwt.encode({'username':user['username']['S'],'exp':datetime.utcnow() + timedelta(minutes=30)},
                           app.config['SECRET_KEY'])
        return jsonify({'token':token})
    
    return jsonify({'message':'Invalid credentials', 'data':{}}), 401


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.current_user = data['username']
        except DecodeError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated_function


@app.route('/upload', methods=['POST'])
@token_required
def upload_data():

    user = request.current_user
    json_data = request.get_json()

    name = json_data['name']
    file_path = json_data['file']
    description = json_data['description']
    tags = json_data['tags']

    try:
        upload(name, file_path, description, tags)
        return jsonify({'message': 'File uploaded successfully!'})

    except Exception as e:
        return jsonify({'message': 'Error occurred while uploading file.', 'error': str(e)}), 500


@app.route('/get', methods=['GET'])
@token_required
def get_data():

    user = request.current_user

    try:
        data = get_from_s3_bucket('user-' + user)
        return data

    except Exception as e:
        return jsonify({'message': 'Error occurred while getting data.', 'error': str(e)}), 500


@app.route('/delete', methods=['DELETE'])
@token_required
def delete_data():

    user = request.current_user
    json_data = request.get_json()
    file = json_data['file']

    try:
        delete_file('user-' + user, file)
        return jsonify({'message': 'File deleted successfully!'})
    except FileNotFoundError as e:
        return jsonify({'message': 'File not found.', 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'message': 'Error occurred while deleting file.', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)