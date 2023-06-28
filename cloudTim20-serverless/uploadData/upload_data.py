from utility.upload import *
import json


def upload_data(event, context):
    token = event['token']
    file_path = event['file_path']
    file_name = event['file_name']
    description = event['description']
    tags = event['tags']

    email = verify_cognito_token(token)
    aws_name = email.split('@')

    try:
        if not tags:
            upload('user-' + aws_name[0], file_path, file_name, description)
        else:
            upload('user-' + aws_name[0], file_path, file_name, description, tags)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'File uploaded successfully!'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error occurred while uploading file.', 'error': str(e)})
        }
