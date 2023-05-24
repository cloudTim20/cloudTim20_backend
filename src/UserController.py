from flask import Flask, jsonify, request, g
from Validation import validate_email, validate_datetime, validate_length
import jwt
from datetime import datetime, timedelta
from upload import *
from datetime import datetime, timedelta
from functools import wraps
from jwt.exceptions import DecodeError
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'


@app.route('/register', methods=['POST'])
def register():
    user = request.get_json()

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


@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization

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
        token = jwt.encode({'username': user['username']['S'], 'exp': datetime.utcnow() + timedelta(minutes=30)},
                           app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials', 'data': {}}), 401


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
            g.current_user = data['username']
        except DecodeError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated_function


@app.route('/upload', methods=['POST'])
@token_required
def upload_data():

    user = g.current_user
    json_data = request.get_json()

    file_path = json_data['file_path']
    file_name = json_data['file_name']
    description = json_data['description']
    tags = json_data['tags']

    try:
        if not tags:
            upload('user-' + user, file_path, file_name, description)
        else:
            upload(user, file_path, file_name, description, tags)
        return jsonify({'message': 'File uploaded successfully!'})

    except Exception as e:
        return jsonify({'message': 'Error occurred while uploading file.', 'error': str(e)}), 500


@app.route('/get', methods=['GET'])
@token_required
def get_data():

    user = g.current_user

    try:
        # data_s3 = get_from_s3_bucket('user-' + user)
        data_dynamodb = get_from_dynamodb_table('user-' + user)
        return data_dynamodb

    except Exception as e:
        return jsonify({'message': 'Error occurred while getting data.', 'error': str(e)}), 500


@app.route('/modify', methods=['PUT'])
@token_required
def modify_data():

    user = request.current_user

    try:
        data = get_from_s3_bucket('user-' + user)
        return data

    except Exception as e:
        return jsonify({'message': 'Error occurred while getting data.', 'error': str(e)}), 500


@app.route('/delete', methods=['DELETE'])
@token_required
def delete_data():

    user = g.current_user
    json_data = request.get_json()
    file = json_data['file']

    try:
        delete_file("user-" + user, file)
        return jsonify({'message': 'File deleted successfully!'})
    except FileNotFoundError as e:
        return jsonify({'message': 'File not found.', 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'message': 'Error occurred while deleting file.', 'error': str(e)}), 500


@app.route('/create-folder', methods=['POST'])
@token_required
def new_folder():

    user = g.current_user
    json_data = request.get_json()
    folder_name = json_data['folder_name']

    try:
        create_folder('user-' + user, folder_name)
        return jsonify({'message': 'Folder created successfully!'})
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return jsonify({'message': 'AWS error', 'error_code': error_code, 'error_message': error_message}), 500
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/delete-folder', methods=['DELETE'])
@token_required
def delete_a_folder():

    user = g.current_user
    json_data = request.get_json()
    folder_name = json_data['folder_name']

    try:
        delete_folder('user-' + user, folder_name)
        return jsonify({'message': 'Folder deleted successfully!'})
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return jsonify({'message': 'AWS error', 'error_code': error_code, 'error_message': error_message}), 500
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/download', methods=['GET'])
@token_required
def download_file():

    user = g.current_user
    json_data = request.get_json()
    file_name = json_data['file_name']
    destination_path = json_data['destination_path']

    try:
        s3_download_file('user-' + user, file_name, destination_path)
        return jsonify({'message': 'File downloaded successfully!'})
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return jsonify({'message': 'AWS error', 'error_code': error_code, 'error_message': error_message}), 500
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/rename-file', methods=['PUT'])
@token_required
def rename():

    user = g.current_user
    json_data = request.get_json()
    old_file_name = json_data['old_file_name']
    new_file_name = json_data['new_file_name']

    try:
        rename_file('user-' + user, old_file_name, new_file_name)
        return jsonify({'message': 'File renamed successfully!'})
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return jsonify({'message': 'AWS error', 'error_code': error_code, 'error_message': error_message}), 500
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/update-metadata', methods=['PUT'])
@token_required
def update_metadata():

    user = g.current_user
    json_data = request.get_json()
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


@app.route('/share', methods=['PUT'])
@token_required
def share_content():

    user = g.current_user
    data = request.get_json()
    content_key = data['content']
    username = data['username']
    table = 'user-' + user

    if(user == username):
        return jsonify({'message': 'Content for your self is already shared'}), 400

    if not user_exists(username):
        return jsonify({'message': 'Recipient user does not exist.'}), 400

    content = get_content_from_database(table, content_key)
    if not content:
        return jsonify({'message': 'Content not found.'}), 404

    try:
        grant_read_permission(table, content_key, username)
        return jsonify({'message': 'Content shared successfully to ' + username})
    except Exception as e:
        return jsonify({'message': str(e)}), 400


@app.route('/revoke', methods=['PUT'])
@token_required
def revoke_permission():

    user = g.current_user
    data = request.get_json()
    content_key = data['content']
    username = data['username']
    table = 'user-' + user

    if(user == username):
        return jsonify({'message': 'Content for your self is already shared'}), 400

    if not user_exists(username):
        return jsonify({'message': 'Recipient user does not exist.'}), 400

    content = get_content_from_database(table, content_key)
    if not content:
        return jsonify({'message': 'Content not found.'}), 404

    try:
        remove_permission(table, content_key, username)
        return jsonify({'message': 'Permission successfully removed from ' + username})
    except Exception as e:
        return jsonify({'message': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
