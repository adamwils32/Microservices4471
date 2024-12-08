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
    ticker3 = params.get('ticker3')
    ticker4 = params.get('ticker4')
    ticker5 = params.get('ticker5')

    if not ticker1 or not ticker2:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request: Both ticker1 and ticker2 are required'})
        }

    # Fetch stock data for both tickers
    try:
        stock1 = get_stock_from_db(ticker1)
        stock2 = get_stock_from_db(ticker2)
        stock3 = get_stock_from_db(ticker3)
        stock4 = get_stock_from_db(ticker4)
        stock5 = get_stock_from_db(ticker5)
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error retrieving stock data', 'error': e.response['Error']['Message']})
        }

    #check if both stocks were found (efficient)
    if stock1 or stock2 or stock3 or stock4 or stock5:
        not_found_tickers = []
        if stock1 is None:
            not_found_tickers.append(ticker1)
        if stock2 is None:
            not_found_tickers.append(ticker2)
        if stock3 is None:
            not_found_tickers.append(ticker3)
        if stock4 is None:
            not_found_tickers.append(ticker4)
        if stock5 is None:
            not_found_tickers.append(ticker5)
        return {
            'statusCode': 404,
            'body': json.dumps({'message': f'Stocks not found: {", ".join(not_found_tickers)}'})
        }
        print(f"Stock1: {stock1}")
        print(f"Stock2: {stock2}")
        print(f"Stock3: {stock3}")
        print(f"Stock4: {stock4}")
        print(f"Stock5: {stock5}")

    # Compare the stock data
    comparison_result = compare_stocks(stock1, stock2, stock3, stock4, stock5)

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
def compare_stocks(stock1, stock2, stock3, stock4, stock5):
    # Define the fields to compare
    fields_to_compare = ['price', 'volume', 'change_percent', 'previous_close', 'change', 'open', 'high', 'low', 'close', 'adj close', 'average close price']

    comparison = {
        'stock1': {'ticker': stock1['ticker']},
        'stock2': {'ticker': stock2['ticker']},
        'stock3': {'ticker': stock3['ticker']},
        'stock4': {'ticker': stock4['ticker']},
        'stock5': {'ticker': stock5['ticker']}
        }

    for field in fields_to_compare:
        value1 = stock1.get(field)
        value2 = stock2.get(field)
        value3 = stock3.get(field)
        value4 = stock4.get(field)
        value5 = stock5.get(field)

        if value1 and value2:
            if value1 is None and value2 is None:
            # ConvertDecimal to float for comparison
                if isinstance(value1, Decimal):
                    value1 = float(value1)
                if isinstance(value2, Decimal):
                    value2 = float(value2)
                if isinstance(value3, Decimal):
                    value3 = float(value3)
                if isinstance(value4, Decimal):
                    value4 = float(value4)
                if isinstance(value5, Decimal):
                    value5 = float(value5)

            comparison['stock1'][field] = value1
            comparison['stock2'][field] = value2
            comparison['stock3'][field] = value3
            comparison['stock4'][field] = value4
            comparison['stock5'][field] = value5

            if value1 > value2:
                result = f'{stock1["ticker"]} has higher {field}'
            elif value1 < value2:
                result = f'{stock2["ticker"]} has higher {field}'
            elif value2 > value3:
                result = f'{stock3["ticker"]} has higher {field}'
            elif value2 < value3:
                result = f'{stock4["ticker"]} has higher {field}'
            elif value3 > value4:
                result = f'{stock5["ticker"]} has higher {field}'
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