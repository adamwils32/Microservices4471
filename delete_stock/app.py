import json
import boto3
from botocore.exceptions import ClientError

# Delete a stock by ticker
def lambda_handler(event, context):

    # ================== inputs ================== #
    # event = {
    #   "httpMethod": "DELETE",
    #   "pathParameters": {
    #       "ticker": "AAPL"
    #   }
    # }
    # ============================================ #

    # Validate the incoming event
    if 'pathParameters' not in event or event['httpMethod'] != 'DELETE':
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request'})
        }

    payload = event['pathParameters']
    ticker = payload.get('ticker')
    ticket = ticket.upper() if ticket else None

    # Check if ticker is provided
    if not ticker:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Ticker symbol is required'})
        }

    # Attempt to delete the stock from the database
    try:
        response = delete_stock_from_db(ticker)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'The stock was deleted successfully from the database'})
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ConditionalCheckFailedException':
            # The stock does not exist
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Stock not found'})
            }
        else:
            # Log and return a generic error
            print(e.response['Error']['Message'])
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'An error occurred while deleting the stock'})
            }

# Delete a selected stock from DynamoDB table using its ticker
def delete_stock_from_db(ticker):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('stocks-table')  # Replace 'stocks-table' with your actual table name

    response = table.delete_item(
        Key={'ticker': ticker},
        ConditionExpression='attribute_exists(ticker)'
    )
    return response