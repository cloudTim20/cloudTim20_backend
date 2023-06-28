try:
    import unzip_requirements
except ImportError:
    pass

import boto3
from dynamodb_json import json_util
import os
import datetime
import botocore
import botocore.exceptions


session = boto3.Session(region_name='eu-central-1')

s3_client = session.client('s3')
s3_resource = session.resource('s3')

dynamodb_client = session.client('dynamodb')
dynamodb_resource = session.resource('dynamodb')

cognito_client = boto3.client('cognito-idp')


def s3_create_bucket(bucket_name):
    s3_client.create_bucket(Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'})


def s3_delete_bucket(bucket_name):
    try:
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting bucket: {e}")


def s3_upload_file(file_path, bucket_name, file_name):
    s3_client.upload_file(file_path, bucket_name, file_name)


def dynamodb_create_table(table_name, pk_name, sk_name=None):
    attribute_definitions = [
        {
            'AttributeName': pk_name,
            'AttributeType': 'S',
        }
    ]
    key_schema = [
        {
            'AttributeName': pk_name,
            'KeyType': 'HASH',
        }
    ]

    if sk_name is not None:
        attribute_definitions.append({
            'AttributeName': sk_name,
            'AttributeType': 'S',
        })
        key_schema.append({
            'AttributeName': sk_name,
            'KeyType': 'HASH',
        })

    provisioned_throughput = {
        'ReadCapacityUnits': 3,
        'WriteCapacityUnits': 3
    }

    dynamodb_client.create_table(TableName=table_name, AttributeDefinitions=attribute_definitions, KeySchema=key_schema,
                                 ProvisionedThroughput=provisioned_throughput)


def dynamodb_delete_table(table_name):
    try:
        table = dynamodb_resource.Table(table_name)
        table.delete()
        print(f"Table '{table_name}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting table: {e}")


def dynamodb_insert_into_table(table_name, item):
    item_json = json_util.dumps(item, as_dict=True)
    dynamodb_client.put_item(TableName=table_name, Item=item_json)


def upload(name, file_path, file_name, description='', tags=None):
    if tags is None:
        tags = []
    s3_upload_file(file_path, name, file_name)

    file, file_extension = os.path.splitext(file_path)
    stat: os.stat_result = os.stat(file_path)

    item = {
        'file_name': file_name,
        'file_type': file_extension,
        'file_size': stat.st_size,
        'created_date': datetime.datetime.fromtimestamp(stat.st_ctime),
        'modified_date': datetime.datetime.fromtimestamp(stat.st_mtime),
        'added_date': datetime.datetime.now(),
        'description': description,
        'tags': tags
    }

    dynamodb_insert_into_table(name, item)


def dynamodb_check_if_exists(table_name, key, value):
    primary_key = {
        key: {"S": value}
    }
    response = dynamodb_client.get_item(
        TableName=table_name,
        Key=primary_key
    )

    if "Item" in response:
        return True
    else:
        return False


def delete_file(username, filename):
    try:

        s3_response = s3_client.head_object(Bucket=username, Key=filename)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            raise FileNotFoundError("File not found in S3 bucket.")
        else:
            raise Exception("Error checking file existence in S3 bucket.")

    try:

        s3_client.delete_object(Bucket=username, Key=filename)
        print("File deleted successfully from S3.")
    except Exception as e:
        raise Exception("Error deleting file from S3: " + str(e))

    try:

        primary_key = {'file_name': {'S': filename}}
        dynamodb_client.delete_item(TableName=username, Key=primary_key)
        print("Item deleted successfully from DynamoDB.")
    except Exception as e:
        raise Exception("Error deleting item from DynamoDB: " + str(e))

    print("File and item deleted successfully.")


def create_folder(username, folder_name):  # vrv treba da se promeni u celu putanju
    s3_client.put_object(
        Bucket=username,
        Key=folder_name + '/'
    )

    pk_name = 'file_name'

    item = {
        pk_name: folder_name,
        'file_type': 'folder',
        'added_date': str(datetime.datetime.now()),
        'description': 'Folder item',
        'tags': []
    }

    dynamodb_insert_into_table(username, item)


def delete_folder(username, folder_name):  # treba da se promeni u celu putanju, ako je folder u folderu

    response = s3_client.list_objects_v2(
        Bucket=username,
        Prefix=folder_name + '/'
    )
    objects = response.get('Contents', [])
    if objects:
        delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objects]}
        s3_client.delete_objects(
            Bucket=username,
            Delete=delete_keys
        )

        delete_file(username, folder_name+'/')


def get_from_dynamodb_table(table_name):
    response = dynamodb_client.scan(
        TableName=table_name,
        FilterExpression='attribute_exists(added_date)',
        ExpressionAttributeNames={
            '#nm': 'file_name',
            '#ty': 'file_type',
            '#sz': 'file_size',
            '#cd': 'created_date',
            '#md': 'modified_date',
            '#ad': 'added_date',
            '#desc': 'description',
            '#tags': 'tags'
        },
        ProjectionExpression='#nm, #ty, #sz, #cd, #md, #ad, #desc, #tags'
    )

    items = response['Items']
    return items


def get_from_s3_bucket(bucket_name):
    response = s3_client.list_objects(Bucket=bucket_name)

    if 'Contents' in response:
        objects = response['Contents']
        return objects
    else:
        return []


def s3_download_file(bucket_name, file_name, destination_path):
    try:
        s3_client.download_file(bucket_name, file_name, destination_path)
        print(f"File '{file_name}' downloaded successfully.")
    except Exception as e:
        print(f"Error downloading file: {e}")


def rename_file(name, old_name, new_name):

    s3_client.copy_object(
        Bucket=name,
        CopySource={'Bucket': name, 'Key': old_name},
        Key=new_name
    )

    s3_client.delete_object(
        Bucket=name,
        Key=old_name
    )

    response = dynamodb_client.get_item(
        TableName=name,
        Key={'file_name': {'S': old_name}}
    )
    item = response['Item']

    dynamodb_client.delete_item(
        TableName=name,
        Key={'file_name': {'S': old_name}}
    )

    item['file_name'] = {'S': new_name}
    dynamodb_client.put_item(
        TableName=name,
        Item=item
    )


def update_item_attribute(table_name, partition_key, attribute_name, new_value):
    update_expression = "SET " + attribute_name + " = :value"
    expression_attribute_values = {
        ":value": {'S': new_value}
    }

    dynamodb_client.update_item(
        TableName=table_name,
        Key={
            'file_name': {'S': partition_key}
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values
    )


def get_content_from_database(table_name, content_id):

    try:
        table = dynamodb_resource.Table(table_name)

        response = table.get_item(Key={'file_name': content_id})

        content_item = response.get('Item')
        if content_item:
            return content_item

    except Exception as e:
        print(f"Error retrieving content from DynamoDB: {e}")

    return None


def get_user_from_database(username):

    table_name = 'users'

    try:
        table = dynamodb_resource.Table(table_name)

        response = table.get_item(Key={'username': username})

        user_item = response.get('Item')
        if user_item:
            return user_item

    except Exception as e:
        print(f"Error retrieving user from DynamoDB: {e}")

    return None


def user_exists(username):
    user = get_user_from_database(username)
    return user is not None


def grant_content_read_permission(table, content_id, username):

    content = get_content_from_database(table, content_id)
    if content:
        if 'content_read_permission' not in content:
            content['content_read_permission'] = []
        if username in content['content_read_permission']:
            raise Exception(username + " already have permission for this content")

    content['content_read_permission'].append(username)
    table = dynamodb_resource.Table(table)
    response = table.update_item(
        Key={'file_name': content_id},
        UpdateExpression='SET content_read_permission = :content_read_permission',
        ExpressionAttributeValues={':content_read_permission': content['content_read_permission']}
    )


def grant_album_read_permission(s3_bucket, username):

    user = get_user_from_database(username)

    if user:
        if 'album_read_permission' not in user:
            user['album_read_permission'] = []
        if s3_bucket in user['album_read_permission']:
            raise Exception(username + " already have permission for this album")

    user['album_read_permission'].append(s3_bucket)
    table = dynamodb_resource.Table("users")
    response = table.update_item(
        Key={'username': username},
        UpdateExpression='SET album_read_permission = :album_read_permission',
        ExpressionAttributeValues={':album_read_permission': user['album_read_permission']}
    )


def remove_content_permission(table, content_id, username):

    content = get_content_from_database(table, content_id)
    if 'content_read_permission' in content and username in content['content_read_permission']:
        content['content_read_permission'].remove(username)
        table = dynamodb_resource.Table(table)
        response = table.update_item(
            Key={'file_name': content_id},
            UpdateExpression='SET content_read_permission = :content_read_permission',
            ExpressionAttributeValues={':content_read_permission': content['content_read_permission']}
        )
    else:
        raise Exception("Permission for this user does not exist")


def remove_album_permission(s3_bucket, username):

    user = get_user_from_database(username)
    if 'album_read_permission' in user and s3_bucket in user['album_read_permission']:
        user['album_read_permission'].remove(s3_bucket)
        table = dynamodb_resource.Table('users')
        response = table.update_item(
            Key={'username': username},
            UpdateExpression='SET album_read_permission = :album_read_permission',
            ExpressionAttributeValues={':album_read_permission': user['album_read_permission']}
        )
    else:
        raise Exception("Permission for this user does not exist")


def check_bucket_existence(bucket_name):

    bucket_exists = True
    try:
        s3_resource.meta.client.head_bucket(Bucket=bucket_name)
    except s3_client.meta.client.exceptions.NoSuchBucket:
        bucket_exists = False

    return bucket_exists


def check_string_contains(string, character):
    if character in string:
        return True
    else:
        return False


def cognito_create_user(email, password):
    user_attributes = [
        {
            'Name': 'email',
            'Value': email
        }
    ]

    response = cognito_client.sign_up(
        ClientId='14sgq6c40ig4h8if1pf07l92e8',
        Username=email,
        Password=password,
        UserAttributes=user_attributes,
        ValidationData=[]
    )

    cognito_client.admin_confirm_sign_up(
        UserPoolId='eu-central-1_Hxi28QRyK',
        Username=email
    )

    return response


def cognito_login(username, password):
    response = cognito_client.initiate_auth(
        ClientId='14sgq6c40ig4h8if1pf07l92e8',
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    )

    return response['AuthenticationResult']['IdToken']

