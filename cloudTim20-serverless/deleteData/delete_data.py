from utility.upload import *
import json


def delete_data(event, context):
    token = event['token']
    file = event['file']

    email = verify_cognito_token(token)
    aws_name = email.split('@')

    try:
        delete_file("user-" + aws_name[0], file)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'File deleted successfully!'})
        }
    except FileNotFoundError as e:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'File not found.', 'error': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error occurred while deleting file.', 'error': str(e)})
        }
