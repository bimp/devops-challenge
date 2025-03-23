
## Notes
- IAM permissions at this early, stage POC phase will be extra permissive. 
Later work would be needed to make the IAM access rights more fine-tuned to 
minimize the IAM blast radius (i.e., specific resource names, remove 
unnecessary access, etc)
- Using IaC code generator from CloudFormation for now. I would have used 
Terraform if I had more time.


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
