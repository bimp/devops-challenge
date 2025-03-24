
## Notes
- IAM permissions at this early, stage POC phase will be extra permissive. 
Later work would be needed to make the IAM access rights more fine-tuned to 
minimize the IAM blast radius (i.e., specific resource names, remove 
unnecessary access, etc)
- Using IaC code generator from CloudFormation for now. I would have used 
Terraform if I had more time.

S3 Bucket Design:
 - Will have one shared S3 bucket for all providers to upload their csv files. 
 - Each provider will have their own folder/prefix in the bucket
 - Assume that a provider will only be allowed to upload files to their own 
 prefix path in the bucket
 - Leverage pre-signed URLs for the providers to upload their files only to 
  their own prefix file path in the bucket
 - Additional resource: https://aws.amazon.com/blogs/storage/design-patterns-for-multi-tenant-access-control-on-amazon-s3/

DynamoDB Table Design:
- Decided to use a partition key for "providerId" to handle multi-tenancy and 
sort key "sortKey" containing the medical_record_number and the date_time in 
the format of "medical_record_number#date_time" to support the querying of a 
specific provider's patient records by medical_record_number and date_time. 
Querying of a specific patient record using the "begins_with" function against 
the sort key which is still performant since it does not trigger a table scan.
- Still creating dedicated fields containg the medical_record_number and 
date_time for possible future use cases without having to parse the values 
from the sort key.


## Questions
1. Should I treat the records in the dynamodb table as immutable? Should the 
table be considered as more a time series log of records with the 
medical_record_number as the primary key?
2. For each customer's csv file, does it represent ALL the records for their 
patients? 
3. Does the pipeline need to timestamp/hash the csv file name being 
uploaded so that there is a unique filename everytime the customer uploads a 
csv file?
4. Can we assume the date_time field in the csv file is in a 
standardized, ISO date format that we would instruct customers to upload 
with? Or does the pipeline need to convert and error out if not in valid format?
