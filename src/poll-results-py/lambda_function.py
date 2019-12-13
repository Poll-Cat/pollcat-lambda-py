import json
import logging
import os
import boto3
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(req, context):

    queryString = req['pathParameters']
    pollid = queryString['pollid']
    
    # Retrieve the name of the DynamoDB table to store connection IDs
    poll_table_name = os.environ['PollTableName']
    
    # Get the Poll from DynamoDB
    dynamodb_client = boto3.client('dynamodb')
    key = {'pollid': {'S': pollid}}
    response = dynamodb_client.get_item(TableName=poll_table_name,
                                        Key=key)
  
    poll = json.dumps(response['Item']['data']['S'])

    # Construct response
    response = {'statusCode': 200, 'body': poll}
    return response
    
