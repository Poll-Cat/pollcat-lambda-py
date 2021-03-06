import json
import logging
import os
import boto3
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    # Log the values received in the event and context arguments
    logger.info('$connect event: ' + json.dumps(event, indent=2))
    logger.info(f'$connect event["requestContext"]["connectionId"]: {event["requestContext"]["connectionId"]}')

    # Retrieve the name of the DynamoDB table to store connection IDs
    table_name = os.environ['ConnectionTableName']

    # Was a pollid specified in a query parameter?
    pollid = ''
    if 'queryStringParameters' in event:
        if 'pollid' in event['queryStringParameters']:
            pollid = event['queryStringParameters']['pollid']

    # Store the connection ID and user name in the table
    item = {'connectionid': {'S': event['requestContext']['connectionId']},
            'pollid': {'S': pollid}}
    dynamodb_client = boto3.client('dynamodb')
    
    try:
        dynamodb_client.put_item(TableName=table_name, Item=item)
    except ClientError as e:
        logger.error(e)
        raise ConnectionAbortedError(e)

    # Construct response
    response = {'statusCode': 200}
    return response
