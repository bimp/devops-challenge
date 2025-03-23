import boto3
import pandas as pd
import os
from botocore.exceptions import ClientError

# Define DynamoDB table name and S3 bucket name
DYNAMODB_TABLE_NAME = "patientRecords"
S3_BUCKET_NAME = "devops-challenge-bparas-patient-records"

# Initialize AWS services
def get_aws_services():
    try:
        # Use environment variables for AWS credentials when running locally
        session = boto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    except:
        # Automatically use IAM role when deployed to Lambda
        session = boto3.Session()
    
    s3 = session.client('s3')
    dynamodb = session.resource('dynamodb')
    return s3, dynamodb

# Function to process CSV file and upload to DynamoDB
def process_csv_file(s3, dynamodb, bucket_name, object_key):
    try:
        # Download the CSV file from S3
        s3.download_file(bucket_name, object_key, '/tmp/' + object_key)
        
        # Read the CSV file
        df = pd.read_csv('/tmp/' + object_key)
        
        # Ensure required columns exist
        required_columns = ['medical_record_number', 'first_name', 'last_name', 'date_time', 'doctors_notes']
        if not all(column in df.columns for column in required_columns):
            print(f"Error: The CSV file {object_key} is missing required columns.")
            return
        
        # Initialize DynamoDB table
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        # Process each row and upload to DynamoDB
        for index, row in df.iterrows():
            try:
                # Check if record already exists to avoid duplicates
                params = {
                    'Key': {
                        'medical_record_number': {'S': medical_record_number}
                }
}
                response = table.get_item(Key={'medical_record_number': row['medical_record_number']})
                if 'Item' in response:
                    print(f"Skipping duplicate record for medical_record_number: {row['medical_record_number']}")
                    continue
                
                # Upload record to DynamoDB
                table.put_item(Item={
                    'medical_record_number': row['medical_record_number'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'date_time': row['date_time'],
                    'doctors_notes': row['doctors_notes']
                })
                print(f"Uploaded record for medical_record_number: {row['medical_record_number']}")
            except ClientError as e:
                print(f"Error uploading record: {e}")
        
        # Clean up temporary file
        os.remove('/tmp/' + object_key)
        
    except Exception as e:
        print(f"Error processing file {object_key}: {e}")

# Function to handle S3 event
def lambda_handler(event, context):
    s3, dynamodb = get_aws_services()
    
    # Process each file in the event
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        if bucket_name == S3_BUCKET_NAME:
            process_csv_file(s3, dynamodb, bucket_name, object_key)

# For local testing
if __name__ == "__main__":
    s3, dynamodb = get_aws_services()
    event = {
        'Records': [
            {
                's3': {
                    'bucket': {
                        'name': S3_BUCKET_NAME
                    },
                    'object': {
                        'key': 'example.csv'
                    }
                }
            }
        ]
    }
    lambda_handler(event, None)
