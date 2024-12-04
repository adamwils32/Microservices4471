import json
import boto3
import uuid
from botocore.exceptions import ClientError

# Extract stock object from request body and insert it into DynamoDB table
def lambda_handler(event, context):

    # ================== Sample Input ================== #
    # event = {
    #     "httpMethod": "POST",
    #     "body": json.dumps({
    #         "ticker": "AAPL",
    #         "company_name": "Apple Inc.",
    #         "exchange": "NASDAQ",
    #         "sector": "Technology"
    #     })
    # }
    # ================================================== #

    # Validate the incoming event
    if 'body' not in event or event['httpMethod'] != 'POST':
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request: Invalid HTTP method or missing body'})
        }

    # Parse the request body
    try:
        new_stock = json.loads(event['body'])
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request: Body is not valid JSON'})
        }

    # Check if required fields are present
    if 'ticker' not in new_stock:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request: Ticker symbol is required'})
        }

    # Add the stock to the database
    try:
        response = add_stock_to_db(new_stock)
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error: Unable to add stock'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'A new stock was saved successfully in the database'})
    }

# Insert a new stock item into DynamoDB table
def add_stock_to_db(new_stock):

    # Assign a unique ID to the stock
    new_stock['id'] = str(uuid.uuid1())

    # Initialize DynamoDB resource and specify the table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('stocks-table')  # Replace 'stocks-table' with your actual table name

    # Put the new stock item into the DynamoDB table
    response = table.put_item(Item=new_stock)
    return response