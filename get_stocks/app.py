import json
import boto3
import decimal
from botocore.exceptions import ClientError


# Get a list of all stocks
def lambda_handler(event, context):
    response = get_stocks_from_db()

    return {
        'statusCode': 200,
        'body': json.dumps(response, indent=2)
    }


# Get a list of all stocks from DynamoDB table
def get_stocks_from_db():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('stocks-table')  # Updated table name

    try:
        response = table.scan()
    except ClientError as e:
        print(e.response['Error']['Message'])
        return []
    else:
        return response.get('Items', [])