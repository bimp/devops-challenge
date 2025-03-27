import boto3
import csv
import os
from io import TextIOWrapper, RawIOBase
from botocore.exceptions import ClientError
from datetime import datetime, timezone

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('medicalRecords')

class S3StreamingBodyWrapper(RawIOBase):
    """Adapter class for StreamingBody to work with TextIOWrapper"""
    def __init__(self, body):
        self.body = body
    
    def readable(self):
        return True
    
    def read(self, size=-1):
        return self.body.read(size)

def record_exists(provider_id, sort_key):
    """Check if a record exists using batch get item"""
    try:
        response = table.get_item(
            Key={
                    'providerId': provider_id, 
                    'sortKey': sort_key
                }
        )
        return 'Item' in response
    except ClientError as e:
        print(f"Existence check error: {e}")
        return True  # Assume exists to prevent duplicates

def process_csv_files(bucket, prefix):
    """Process all CSV files in a given S3 prefix using streaming"""
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
    
    for page in page_iterator:
        if 'Contents' not in page:
            continue
            
        for obj in page['Contents']:
            if not obj['Key'].endswith('.csv'):
                continue
                
            provider_id = obj['Key'].split('/')[0]
            csv_filename = obj['Key'].split('/')[1]
            process_single_file(bucket, obj['Key'], provider_id, csv_filename)

def process_single_file(bucket, key, provider_id, csv_filename):
    """Process CSV with existence checks before batch writing"""
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        wrapped_body = S3StreamingBodyWrapper(response['Body'])
        text_stream = TextIOWrapper(wrapped_body, encoding='utf-8')
        
        with table.batch_writer() as batch:
            for row in csv.DictReader(text_stream):
                if not is_valid_row(row):
                    print(f"Skipping invalid row: {row}")
                    continue
                
                sort_key = f"{row['medical_record_number']}#{row['date_time']}"
                
                # Skip existing records
                # have to use a record_exists check since can not do 
                # conditional writes in a batch write operation
                if record_exists(provider_id, sort_key):
                    print(f"Skipping existing: {sort_key}")
                    continue
                
                # Get local time with offset
                dateTimeProcessed = datetime.now().astimezone().isoformat()
                
                # Prepare new item
                item = {
                    'providerId': provider_id,
                    'sortKey': sort_key,
                    'medicalRecordNumber': row['medical_record_number'],
                    'firstName': row['first_name'],
                    'lastName': row['last_name'],
                    'dateTime': row['date_time'],
                    'doctorsNotes': row['doctors_notes'],
                    'dateTimeProcessed': dateTimeProcessed,
                    'csvFile': csv_filename
                }
                
                # Add to batch
                batch.put_item(Item=item)
                print(f"Queued for insert: {sort_key}")
                
    except ClientError as e:
        print(f"S3 Error: {e}")

def is_valid_row(row):
    """
    Validate if the row has a valid date_time in ISO 8601 format with timezone offset.
    """
    date_time = row.get('date_time')
    if not date_time:
        return False
    try:
        dt = datetime.fromisoformat(date_time)
        # Ensure 'T' is present and timezone offset exists
        return 'T' in date_time and (dt.tzinfo is not None)
    except ValueError:
        return False

def lambda_handler(event, context):
    """Handle S3 trigger events"""
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        prefix = '/'.join(key.split('/')[:-1]) + '/'
        
        process_csv_files(bucket, prefix)
    
    return {
        'statusCode': 200,
        'body': 'CSV processing completed'
    }

if __name__ == "__main__":
    # Local test configuration
    test_bucket = "devops-challenge-bparas-patient-records"
    
    # Test with known existing record
    # print(record_exists('hospital01', 'ABC123#2025-03-23T17:20:00-07:00'))  # Should return True
    # # Test with non-existent record
    # print(record_exists('test-provider', '000000#2099-01-01T00:00:00-00:00'))  # Should return False

    process_csv_files(test_bucket, "hospital01/")
    
    process_csv_files(test_bucket, "hospital02/")
