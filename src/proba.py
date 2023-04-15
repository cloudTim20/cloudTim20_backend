import boto3

client = boto3.client('s3')
s3 = boto3.resource('s3')

def s3_create_bucket(bucket_name):
    client.create_bucket(Bucket = bucket_name,
                         CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'})

def s3_upload_file(file_path, bucket_name, file_name):
    client.upload_file(file_path, bucket_name, file_name)
