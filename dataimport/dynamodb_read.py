import boto3

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')

# Define table name and key
table_name = 'patientRecords'
medical_record_number = 'ABC123'

# Define the key with the correct data type
key = {
    'medical_record_number': {'S': medical_record_number}
}

# Get item parameters
params = {
    'TableName': table_name,
    'Key': key
}

try:
    # Get the item
    response = dynamodb.get_item(**params)
    
    if 'Item' in response:
        print("Item found:")
        print(response['Item'])
    else:
        print("Item not found.")
except Exception as e:
    print(f"An error occurred: {e}")
