
## frontend and middletier Architecture

![s3-upload-lambda](devops-challenge-part2.drawio.svg)

## Notes
- got the frontend/middletier working locally with successful connection to 
 the dynamodb table
- able to query the records via the /items API call
- able to package both frontend and middletier applications into Docker 
images/containers. Then was able to upload these images into ECR and have it 
deploy into an ALB/Targetgroup/Fargate stack with requisite IAM roles, security 
group
- However, I get a browser error when attempting to hit my ALB A record address 
with the exposed port 3000. Initial web page does come up but then I get some 
error where the browser is attempting to hit the ALB A record to port 8000
- frontend and middletier are packaged as a single Fargate service so localhost 
 references can be kept intact for service-to-service communication
- ALB only exposes http port 3000 to public

## Improvements
- deploy Fargate services in private subnet and allow public traffic via ALB 
deployed in public subnet. 
- further refine/minimize IAM access rights to limit blast radius for better 
security
- the startup of the frontend application can be further minimized by packaging 
dependencies within local Docker container




