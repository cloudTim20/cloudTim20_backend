from utility.upload import *
import json


def new_folder(event, context):
    token = event['token']
    folder_name = event['folder_name']

    email = verify_cognito_token(token)
    aws_name = email.split('@')

    try:
        create_folder('user-' + aws_name[0], folder_name)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Folder created successfully!'})
        }
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'AWS error', 'error_code': error_code, 'error_message': error_message})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'An error occurred', 'error': str(e)})
        }
