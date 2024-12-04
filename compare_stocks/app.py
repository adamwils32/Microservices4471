import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

# Compare two stocks by their ticker symbols
def lambda_handler(event, context):

    # Validate the incoming event
    if 'queryStringParameters' not in event or event['httpMethod'] != 'GET':
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request: Missing query parameters or invalid HTTP method'})
        }

    params = event['queryStringParameters']
    ticker1 = params.get('ticker1')
    ticker2 = params.get('ticker2')

    if not ticker1 or not ticker2:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request: Both ticker1 and ticker2 are required'})
        }

    # Fetch stock data for both tickers
    try:
        stock1 = get_stock_from_db(ticker1)
        stock2 = get_stock_from_db(ticker2)
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error retrieving stock data', 'error': e.response['Error']['Message']})
        }

    # Check if both stocks were found
    if not stock1 or not stock2:
        not_found_tickers = []
        if not stock1:
            not_found_tickers.append(ticker1)
        if not stock2:
            not_found_tickers.append(ticker2)
        return {
            'statusCode': 404,
            'body': json.dumps({'message': f'Stocks not found: {", ".join(not_found_tickers)}'})
        }

    # Compare the stock data
    comparison_result = compare_stocks(stock1, stock2)

    return {
        'statusCode': 200,
        'body': json.dumps(comparison_result, default=handle_decimal_type)
    }

# Retrieve a stock's data from DynamoDB
def get_stock_from_db(ticker):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('stocks-table')  # Replace with your actual table name

    try:
        response = table.get_item(Key={'ticker': ticker})
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e

    return response.get('Item')

# Compare two stock data dictionaries
def compare_stocks(stock1, stock2):
    # Define the fields to compare
    fields_to_compare = ['price', 'volume', 'change_percent']

    comparison = {
        'stock1': {'ticker': stock1['ticker']},
        'stock2': {'ticker': stock2['ticker']},
        'comparisons': {}
    }

    for field in fields_to_compare:
        value1 = stock1.get(field)
        value2 = stock2.get(field)

        if value1 is not None and value2 is not None:
            # Convert Decimal to float for comparison
            if isinstance(value1, Decimal):
                value1 = float(value1)
            if isinstance(value2, Decimal):
                value2 = float(value2)

            comparison['stock1'][field] = value1
            comparison['stock2'][field] = value2

            if value1 > value2:
                result = f'{stock1["ticker"]} has higher {field}'
            elif value1 < value2:
                result = f'{stock2["ticker"]} has higher {field}'
            else:
                result = f'Both stocks have equal {field}'

            comparison['comparisons'][field] = result
        else:
            comparison['comparisons'][field] = 'Data not available for comparison'

    return comparison

# Handle Decimal types for JSON serialization
def handle_decimal_type(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    raise TypeError