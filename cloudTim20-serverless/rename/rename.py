from utility.upload import *
import json


def rename(event, context):
    token = event['token']
    old_file_name = event['old_file_name']
    new_file_name = event['new_file_name']

    email = verify_cognito_token(token)
    aws_name = email.split('@')

    try:
        rename_file('user-' + aws_name[0], old_file_name, new_file_name)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'File renamed successfully!'})
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
