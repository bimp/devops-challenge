import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')

# Define table name and key
table_name = 'medicalRecords'

try:
    # Get specific item
    print("Getting specific item...")
    provider_id = 'hospital01'
    sort_key = 'ABC123#2025-03-23T17:20:00-07:00'
    # Define the key with the correct data type
    key = {
        'providerId': {'S': provider_id}, 
        'sortKey': {'S':sort_key}
    }
    # Get item parameters
    params = {
        'TableName': table_name,
        'Key': key
    }
    response = dynamodb.get_item(**params)
    if 'Item' in response:
        print("Item found:")
        print(response['Item'])
    else:
        print("Item not found.")
        
    # Get multiple records for a specific partition key and sort key condition
    print("\nGetting multiple items...")
    dynamodb = boto3.resource('dynamodb')
    provider_id = 'hospital02'
    sortkey_prefix = 'MR5005#'
    
    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression=Key('providerId').eq(provider_id) 
        & Key('sortKey').begins_with(sortkey_prefix)
    )
    
    if not response['Items']:
        print("No items found.")
    else:
        for item in response['Items']:
            print(item)
        
except Exception as e:
    print(f"An error occurred: {e}")
