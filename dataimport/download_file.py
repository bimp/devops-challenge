import boto3

# Initialize S3 client
s3 = boto3.client('s3', region_name='us-east-1')

# Define bucket and key
bucket_name = 'devops-challenge-bparas-patient-records'
object_key = 'example.csv'
local_filename = '/tmp/example.csv'

try:
    # Download the file
    s3.download_file(bucket_name, object_key, local_filename)
    print(f"Downloaded {object_key} to {local_filename}")
except Exception as e:
    print(f"Error downloading file: {e}")
