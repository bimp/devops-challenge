
## Customer Patient Records CSV Uploading to DynamoDB Pipeline

![s3-upload-lambda](devops-challenge-part1.drawio.svg)

## Notes and Improvements
 - At this point, have a [lambda_function.py](lambda_function.py) 
 running locally to populate dynamodb table.
 - multi-tenancy handled via a S3 prefix path and providerId field in DynamoDB 
 table
 - still need to add more record validation
 - still need to deploy Lambda function and implement the S3 to Lambda trigger

---
 - In Steps 1 and 2, the application will know the providerId to help generate the initial s3 csv artifact file path
 - Step 3 will return the s3 signed url path to the user with Put 
 operation writes to overwrite the file in Step 4.
    - This auto generated file path will have a unique date,time,hash file name so that user can never overwrite a previously uploaded file
    - Each provider/hospital will only ever have access to their own specific provider S3 prefix path
    - this initial seeded file will be placed in the /providerId/uploaded/ path
 - In Step 5, Lambda function will trigger and process the file. 
 Processing the file may include any or all of the following depending on requirements:
    - extract the providerId from the s3 prefix path to be used in writing to DynamoDB
    - "move/copy/rename" csv upload to /providerId/processing/ path
    - parse csv file and write to DynamoDB in Step 6
    - upon successful completion, "move/copy/rename" csv file to 
    /providerId/completed/
 - In Step 6, writing to DynamoDB should include the following logic:
    - record the csv filename so that there can be an audit record back to the original csv file 
    - idempotent record creation based on record existence check of user 
    provided medical_record_number and date_time
    

 ## S3 Notes
 - make sure public read access disabled
 - only allow secure https transport protocol
 - apply an appropriate life cycle property to comply with GDPR and HIPAA 
 
 ## DynamoDB Table Structure
- providerId as partition key with the sortKey containing the following 
    format: medicalRecordNumber#dateTime
        - this allows the optimized read access pattern of a doctor pulling up 
        patient records in chronological order usign the query "begins with" call.
        - this allows for performannt queries since a table scan is avoided
        - still store the dateTime and medical Record number in dedicated fields 
        for other query/reporting purposes

| providerId | sortKey | dateTime | doctorsNotes | dateTimeProcessed | csvFile | firstName | lastName | medicalRecordNumber |
|------------|---------|----------|--------------|-------------------|---------|-----------|----------|---------------------|
| PROV001 | 2025-03-26#12345 | 2025-03-26T10:30:00-07:00 | Patient reports mild fever | 2025-03-26T11:15:00-07:00 | records_20250326.csv | John | Doe | MRN123456 |
| PROV002 | 2025-03-26#67890 | 2025-03-26T14:45:00-07:00 | Follow-up on previous treatment | 2025-03-26T15:30:00-07:00 | records_20250326.csv | Jane | Smith | MRN789012 |
| PROV003 | 2025-03-26#24680 | 2025-03-26T09:15:00-07:00 | Annual check-up, all clear | 2025-03-26T10:00:00-07:00 | records_20250326.csv | Bob | Johnson | MRN345678 |



