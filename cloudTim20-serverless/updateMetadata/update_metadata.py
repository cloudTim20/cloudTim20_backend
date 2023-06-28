from utility.upload import *
import json


def update_metadata(event, context):
    token = event['token']
    file_name = event['file_name']
    attribute = event['attribute']
    value = event['value']

    email = verify_cognito_token(token)
    aws_name = email.split('@')

    try:
        update_item_attribute('user-' + aws_name[0], file_name, attribute, value)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': "File's metadata updated successfully!"})
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
