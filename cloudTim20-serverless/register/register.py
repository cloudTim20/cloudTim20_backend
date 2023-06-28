try:
    import unzip_requirements
except ImportError:
    pass

from utility.upload import *
from utility.Validation import *
import json


def register(event, context):

    name = event['name']
    surname = event['surname']
    username = event['username']
    birth_date = event['birth_date']
    email = event['email']
    password = event['password']

    if not validate_datetime(birth_date):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid datetime format for birth_date.'})
        }

    if not validate_email(email):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid email format.'})
        }

    if not validate_length(name, 2, 50):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid name length.'})
        }

    if not validate_length(surname, 2, 50):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid surname length.'})
        }

    if not validate_length(username, 2, 50):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid username length.'})
        }

    if not validate_length(email, 6, 50):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid email length.'})
        }

    if not validate_length(password, 6, 50):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid password length.'})
        }

    if dynamodb_check_if_exists('users', 'username', username):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Username is already taken.'})
        }

    dynamodb_insert_into_table('users', event)

    aws_name = email.split('@')

    s3_create_bucket("user-" + aws_name[0])
    dynamodb_create_table("user-" + aws_name[0], "file_name")

    cognito_create_user(email, password)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'User registered successfully!'})
    }
