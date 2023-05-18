import boto3
from dynamodb_json import json_util
import os
import datetime

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

dynamodb_client = boto3.client('dynamodb')

def s3_create_bucket(bucket_name):
    s3_client.create_bucket(Bucket = bucket_name,
                         CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'})

def s3_upload_file(file_path, bucket_name, file_name):
    s3_client.upload_file(file_path, bucket_name, file_name)

def dynamodb_create_table(table_name, pk_name, sk_name = None):
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

    if sk_name != None:
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

    dynamodb_client.create_table(TableName = table_name, AttributeDefinitions = attribute_definitions, KeySchema = key_schema, ProvisionedThroughput = provisioned_throughput)

def dynamodb_insert_into_table(table_name, item):
    item_json = json_util.dumps(item, as_dict=True)
    dynamodb_client.put_item(TableName = table_name, Item = item_json)

def upload(name, file_path, file_name, description = '', tags=None):
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
        'descrioption': description,
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
        return True  # Item exists
    else:
        return False  # Item does not exist

# s3_create_bucket('final-test-123')
# dynamodb_create_table('users', 'username')

# upload('final-test-123', 'C:/Users/Svetozar/Desktop/download.png', 'download', 'opis')

# primary_key = {
#     "file_name": {"S": "download"}
# }
# print(dynamodb_client.get_item(TableName='final-test-123',
#     Key=primary_key))

# print(dynamodb_check_if_exists('final-test-123', 'file_name', 'hhh'))