from utility.upload import *
import json


def share_album(event, context):
    token = event['token']
    album = event['album']
    username = event['username']

    email = verify_cognito_token(token)
    aws_name = email.split('@')

    # table = 'user-' + aws_name[0]

    if (check_string_contains(album, '-') is False) or check_bucket_existence(album) is False:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Album does not exist.'})
        }

    # if (user == username) or (album.split('-')[1] == username):
    #     return jsonify({'message': 'Album for your self is already shared'}), 400

    if not user_exists(username):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Recipient user does not exist.'})
        }

    try:
        grant_album_read_permission(album, username)
        return {
            'statusCode': 200,
            'body': json.dumps({'message':'Album shared successfully to ' + username})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'An error has occurred.', 'error': str(e) })
        }
