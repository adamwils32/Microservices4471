import json
from flask import Flask, jsonify, request
import boto3
from botocore.exceptions import BotoCoreError, ClientError

app = Flask(__name__)

# Initialize the AWS Service Discovery client
client = boto3.client('servicediscovery')

@app.route('/discover-services', methods=['GET'])
def discover_services():
    """
    Endpoint to discover services in a given namespace.
    Expects `namespaceId` as a query parameter.
    Returns a list of discovered services.
    """
    namespace_id = request.args.get('namespaceId')

    if not namespace_id:
        return jsonify({"error": "Missing 'namespaceId' query parameter"}), 400

    try:
        response = client.list_services(Filters=[
            {
                'Name': 'NAMESPACE_ID',
                'Values': [namespace_id],
                'Condition': 'EQ'
            }
        ])

        services = response.get('Services', [])
        service_list = [
            {
                'Id': service['Id'],
                'Name': service['Name'],
                'Description': service.get('Description', ''),
            }
            for service in services
        ]

        # Return the response with CORS headers
        return jsonify({"services": service_list}), 200

    except (BotoCoreError, ClientError) as e:
        return jsonify({"error": str(e)}), 500

# Lambda handler for AWS integration
def lambda_handler(event, context):
    # Log the incoming event to inspect its structure
    print("Event received:", event)

    # Use .get() to handle missing keys gracefully
    path = event.get('path', '/default-path')
    query_string = event.get('queryStringParameters', {})

    # Check if the required query parameter is present in the event
    with app.test_request_context(path=path, query_string=query_string):
        response = app.full_dispatch_request()

    # Adding CORS headers to the response
    response_data = {
        'statusCode': response.status_code,
        'body': response.get_data(as_text=True),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Allow all origins, or specify your front-end URL
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',  # Allow methods like GET, POST, OPTIONS
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'  # Allow headers you expect
        }
    }

    return response_data
