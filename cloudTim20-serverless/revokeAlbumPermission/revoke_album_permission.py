from utility.upload import *
import json


def revoke_album_permission(event, context):
    token = event['token']
    album = event['album']
    username = event['username']

    if (check_string_contains(album, '-') is False) or check_bucket_existence(album) is False:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Album does not exist.'})
        }

    # if user == username:
    #     return jsonify({'message': 'Album for your self is already shared'}), 400

    if not user_exists(username):
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Recipient user does not exist.'})
        }

    try:
        remove_album_permission(album, username)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Permission successfully removed from ' + username})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'An error has occurred.', 'error': str(e) })
        }
