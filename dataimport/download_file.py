import boto3
import os

s3 = boto3.client('s3')

bucket_name = 'devops-challenge-bparas-patient-records'
object_key = 'hospital01/example.csv'
local_file_name = '/tmp/hospital01/example.csv'

# Create the directory if it doesn't exist
os.makedirs(os.path.dirname(local_file_name), exist_ok=True)

s3.download_file(bucket_name, object_key, local_file_name)
