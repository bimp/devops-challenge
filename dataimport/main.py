import boto3
import pandas as pd
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('patientRecords')

def parse_provider_id(object_key):
    return object_key.split('/')[0]

def load_csv_from_s3(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return pd.read_csv(response['Body'])
    except (ClientError, pd.errors.ParserError) as e:
        print(f"Error loading CSV: {e}")
        return None

def process_csv(df, provider_id):
    for _, row in df.iterrows():
        sort_key = f"{row['medical_record_number']}#{row['date_time']}"
        try:
            table.put_item(
                Item={
                    'providerId': provider_id,
                    'sortKey': sort_key,
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'date_time': row['date_time'],
                    'doctors_notes': row['doctors_notes']
                },
                ConditionExpression='attribute_not_exists(sortKey)',
                ReturnValuesOnConditionCheckFailure='ALL_OLD'
            )
            print(f"Inserted record: {provider_id}/{sort_key}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"Duplicate skipped: {provider_id}/{sort_key}")
            else:
                print(f"DynamoDB Error: {e}")

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        provider_id = parse_provider_id(key)
        
        if (df := load_csv_from_s3(bucket, key)) is not None and not df.empty:
            process_csv(df, provider_id)
    
    return {'statusCode': 200, 'body': 'Processing complete'}

# for local testing
if __name__ == "__main__":
    # Test with mock event
    test_event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "devops-challenge-bparas-patient-records"},
                "object": {"key": "hospital01/example.csv"}
            }
        }]
    }
    
    # First run (successful insert)
    lambda_handler(test_event, None)
    
    # Second run (duplicate handling)
    lambda_handler(test_event, None)

