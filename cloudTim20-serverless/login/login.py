from utility.upload import *
import json


def login(event, context):
    username = event['email']
    password = event['password']

    try:
        token = cognito_login(username, password)

        return {
            'statusCode': 200,
            'body': json.dumps({'token': token})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e)
        }
