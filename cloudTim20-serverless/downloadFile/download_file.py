from utility.upload import *
import json


def download_file(event, context):
    token = event['token']
    file_name = event['file_name']
    destination_path = event['destination_path']

    email = verify_cognito_token(token)
    aws_name = email.split('@')

    try:
        s3_download_file('user-' + aws_name[0], file_name, destination_path)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'File downloaded successfully!'})
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
