import json
import logging
import os
import boto3
import uuid
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(poll, context):
    
    # Retrieve the name of the DynamoDB table to store connection IDs
    poll_table_name = os.environ['PollTableName']
    
    # Create a new GUID for the pollid
    pollid = str(uuid.uuid4())
    
    poll['pollid'] = pollid
    logger.info('poll:')
    logger.info(poll)
    # Save the Poll to DynamoDB
    dynamodb_client = boto3.client('dynamodb')
        
    item = {'pollid': {'S': pollid},
            'data': {'S': json.dumps(poll)}
    }
    
    try:
        dynamodb_client.put_item(TableName=poll_table_name, Item=item)
    except ClientError as e:
        logger.error(e)
        raise ValueError(e)

    # Construct response
    response = {'statusCode': 200, 'body': pollid}
    return response
    