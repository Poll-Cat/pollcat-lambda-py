import json
import logging
import os
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

# Set up logging
logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(req, context):

    vote = json.loads(req['body'])
    
    # Retrieve the name of the DynamoDB table to store connection IDs
    poll_table_name = os.environ['PollTableName']
    
    # Get the Poll from DynamoDB
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_resouce = boto3.resource('dynamodb')
    
    key = {'pollid': {'S': vote['pollid']}}
    response = dynamodb_client.get_item(TableName=poll_table_name,
                                        Key=key)
  
    poll = json.loads(response['Item']['data']['S'])
    pollid = poll['pollid']
    
    # Update the VoteCount for the selected option(s)
    for choice in vote['options']:
        selectedOption = poll['options'][choice]
        currentVoteCount = selectedOption['optionVotes']
        newVoteCount = currentVoteCount + 1
        selectedOption['optionVotes'] = newVoteCount
    
    # Save the Poll to DynamoDB
    item = {'pollid': {'S': poll['pollid']},
            'data': {'S': json.dumps(poll)}
    }
    
    try:
        dynamodb_client.put_item(TableName=poll_table_name, Item=item)
    except ClientError as e:
        logger.error(e)
        raise ValueError(e)

    # Retrieve the name of the DynamoDB table to store connection IDs
    connection_table_name = os.environ['ConnectionTableName']
    connection_table = dynamodb_resouce.Table(connection_table_name)
    
    # Retrieve all connection IDs from the table
    try:
        response = connection_table.scan(FilterExpression=Key('pollid').eq(pollid))
    except ClientError as e:
        logger.error(e)
        raise ValueError(e)
        
    connectionsData = response['Items']
        
    while 'LastEvaluatedKey' in response:
        response = connection_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'],
                                        ilterExpression=Key('pollid').eq(pollid))
        connectionsData.extend(response['Items'])

    # Construct the message text as bytes
    body = json.dumps(poll)
    message = body.encode('utf-8')

    # Send the message to each connection
    session = boto3.session.Session()
    
    api_client = session.client(
        service_name='apigatewaymanagementapi',
        endpoint_url='https://4jhdjfts22.execute-api.us-east-2.amazonaws.com/alpha/'
    )

    for item in connectionsData:
        connectionId = item['connectionid']
        try:
            apiResponse = api_client.post_to_connection(Data=message,
                                          ConnectionId=connectionId)
            logger.info(apiResponse)
        except ClientError as e:
            logger.error(e)

    # Construct response
    response = {'statusCode': 200}
    return response
