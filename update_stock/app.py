import json
import boto3
import os
import urllib.request
from decimal import Decimal
from botocore.exceptions import ClientError

# Update a stock's data based on the latest information from Alpha Vantage API
def lambda_handler(event, context):

    # Validate the incoming event
    if 'pathParameters' not in event or event['httpMethod'] != 'PUT':
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request: Missing path parameters or invalid HTTP method'})
        }

    ticker = event['pathParameters'].get('ticker')
    if not ticker:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request: Missing stock ticker in path parameters'})
        }

    # Fetch the latest stock data from Alpha Vantage API
    try:
        stock_data = get_latest_stock_data(ticker)
    except Exception as e:
        print(f"Error fetching data for ticker {ticker}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error fetching data from Alpha Vantage API', 'error': str(e)})
        }

    # Update the stock data in DynamoDB
    try:
        response = update_stock_in_db(ticker, stock_data)
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error updating stock data in DynamoDB', 'error': e.response['Error']['Message']})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Stock data was updated successfully in the database'})
    }

# Fetch the latest stock data from Alpha Vantage API
def get_latest_stock_data(ticker):

    # Get the Alpha Vantage API key from environment variables
    api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
    if not api_key:
        raise Exception('Alpha Vantage API key is not set in environment variables')

    # Build the Alpha Vantage API URL
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}'

    # Fetch data from the Alpha Vantage API
    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                raise Exception(f'HTTP Error {response.status}')
            data = response.read()
    except urllib.error.HTTPError as e:
        raise Exception(f'HTTP Error: {e.code} {e.reason}')
    except urllib.error.URLError as e:
        raise Exception(f'URL Error: {e.reason}')

    # Parse the JSON response
    data_json = json.loads(data)

    # Check for API call frequency limit exceeded
    if 'Note' in data_json:
        raise Exception('API call frequency exceeded. Please wait a minute and try again.')

    # Extract the 'Global Quote' data
    if 'Global Quote' not in data_json or not data_json['Global Quote']:
        raise Exception('Invalid response from Alpha Vantage API or stock ticker not found')

    stock_data = data_json['Global Quote']

    return stock_data

# Update the stock data in DynamoDB
def update_stock_in_db(ticker, stock_data):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('stocks-table')  # Replace with your actual table name

    # Map the Alpha Vantage data to DynamoDB item attributes
    item = {
        'ticker': ticker,
        'price': stock_data.get('05. price'),
        'volume': stock_data.get('06. volume'),
        'latest_trading_day': stock_data.get('07. latest trading day'),
        'previous_close': stock_data.get('08. previous close'),
        'change': stock_data.get('09. change'),
        'change_percent': stock_data.get('10. change percent'),
        # Add other fields as needed
    }

    # Remove any None values from the item
    item = {k: v for k, v in item.items() if v is not None}

    # Convert numeric string values to Decimal
    numeric_fields = ['price', 'volume', 'previous_close', 'change']
    for key in numeric_fields:
        if key in item and item[key]:
            # Convert string to Decimal
            item[key] = Decimal(item[key])

    # Update the item in DynamoDB
    response = table.put_item(Item=item)

    return response