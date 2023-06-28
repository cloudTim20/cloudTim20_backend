from utility.upload import *
import json


def modify_data(event, context):
    token = event['token']

    email = verify_cognito_token(token)
    aws_name = email.split('@')

    try:
        data = get_from_s3_bucket('user-' + aws_name[0])
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data successfully modified!'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error occurred while getting data.', 'error': str(e)})
        }
