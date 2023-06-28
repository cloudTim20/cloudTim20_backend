from utility.upload import *
import json


def share_content(event, context):
    token = event['token']
    content_key = event['content']
    username = event['username']

    email = verify_cognito_token(token)
    aws_name = email.split('@')

    table = 'user-' + aws_name[0]

    # if user == username:
    #     return jsonify({'message': 'Content for your self is already shared'}), 400

    if not user_exists(username):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Recipient user does not exist.'})
        }

    content = get_content_from_database(table, content_key)
    if not content:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Content not found.'})
        }

    try:
        grant_content_read_permission(table, content_key, username)
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Content shared successfully to ' + username})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'An error has occurred.', 'error': str(e) })
        }
