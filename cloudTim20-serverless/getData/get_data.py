from utility.upload import *
import json


def get_data(event, context):

    token = event['token']

    email = verify_cognito_token(token)
    aws_name = email.split('@')

    try:
        # data_s3 = get_from_s3_bucket('user-' + user)
        data_dynamodb = get_from_dynamodb_table('user-' + aws_name[0])
        return {
            'statusCode': 200,
            'body': json.dumps({'data': data_dynamodb})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error occurred while getting data.', 'error': str(e)})
        }



