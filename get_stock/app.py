import json
import boto3
import decimal
from botocore.exceptions import ClientError

def lambda_handler(event, context):

    # Validate the incoming event
    if 'pathParameters' not in event or event['httpMethod'] != 'GET':
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request'})
        }

    # Extract the stock ticker from the path parameters
    ticker = event['pathParameters']['ticker']

    # Fetch the stock data from DynamoDB
    response = get_stock_from_db(ticker)

    # Handle the case where the stock is not found
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Stock not found'})
        }

    # Return the stock data
    return {
        'statusCode': 200,
        'body': json.dumps(response['Item'], indent=2)
    }

def get_stock_from_db(ticker):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('stocks-table')  # Replace with your actual table name

    try:
        response = table.get_item(Key={'ticker': ticker})
        return response
    except ClientError as e:
        print(e.response['Error']['Message'])
        # Consider returning an error response here if needed
        raise e