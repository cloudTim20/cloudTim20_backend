import boto3
from dynamodb_json import json_util
import os
import datetime

session = boto3.Session(region_name='eu-central-1')

s3_client = session.client('s3')
s3_resource = session.resource('s3')

dynamodb_client = session.client('dynamodb')


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

    dynamodb_client.create_table(TableName=table_name, AttributeDefinitions=attribute_definitions, KeySchema=key_schema,
                                 ProvisionedThroughput=provisioned_throughput)


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


def delete_file(username, filename):  # vrv treba da se promeni u celu putanju
    try:
        s3_client.delete_object(Bucket=username, Key=filename)
        print("File deleted successfully from s3.")
    except Exception as e:
        print("Error deleting file from s3:", str(e))

    try:
        primary_key = {
            'file_name': {
                'S': filename
            }
        }
        dynamodb_client.delete_item(
            TableName=username,
            Key=primary_key
        )
        print("Item deleted successfully from dynamodb.")
    except Exception as e:
        print("Error deleting item from dynamodb:", str(e))


# Example usage
# bucket_name = 'proba-123-321'
# item_key = 'cloud_todo'
# delete_file(bucket_name, item_key)


def create_folder(username, folder_name):  # vrv treba da se promeni u celu putanju
    s3_client.put_object(
        Bucket=username,
        Key=folder_name + '/'
    )
    #kreirati i u dynamodb
    #dodavanje obicnog fajla u dynamodb isto cela putanja
    #premestanje fajlova u nove foldere
    
#create_folder('user-andrea01', 'prvi_folder')

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
        #obrisati i sve fajlove iz tog foldera iz dynamodb

#delete_folder('user-andrea01', 'prvi_folder')


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


# print(get_from_dynamodb_table("proba-123-321"))
# print(get_from_s3_bucket('proba-123-321'))
# s3_create_bucket('final-test-123')
# dynamodb_create_table('usersssss', 'username')
# upload('user-andrea01', 'C:/Users/andre/OneDrive/Desktop/VSEM.txt', 'vsem', 'opissss')
#create_folder("user-andrea01", "novi_folder")
# dynamodb_create_table('proba-123-321', 'file_name')
# s3_create_bucket('proba-123-321')
# upload('proba-123-321', 'C:/Users/Svetozar/Desktop/cloud_todo.txt', 'cloud_todo', 'opis')

# primary_key = {
#     "file_name": {"S": "download"}
# }
# print(dynamodb_client.get_item(TableName='final-test-123',
#     Key=primary_key))

# print(dynamodb_check_if_exists('final-test-123', 'file_name', 'hhh'))



# Filip {

# Kreiranje s3 bucketa
# s3_create_bucket('filipkralj-test-123')

# Brisanje s3 bucketa
# s3_delete_bucket('filipkralj-test-123')




# Kreiranje bucketa


