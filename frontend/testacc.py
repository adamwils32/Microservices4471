import boto3
import json

def invoke_function_in_namespace(namespace_id, service_name, payload):
    client = boto3.client('servicediscovery')
    lambda_client = boto3.client('lambda')

    # Step 1: Discover services
    services = client.list_services(
        Filters=[{'Name': 'NAMESPACE_ID', 'Values': [namespace_id]}]
    )['Services']
    service = next((s for s in services if s['Name'] == service_name), None)

    if not service:
        raise ValueError(f"Service {service_name} not found in namespace {namespace_id}")

    # Step 2: Discover instances
    instances = client.list_instances(ServiceId=service['Id'])['Instances']
    for instance in instances:
        function_arn = instance['Attributes'].get('lambdaARN')
        if function_arn:
            # Step 3: Invoke the Lambda function
            response = lambda_client.invoke(
                FunctionName=function_arn,
                InvocationType='RequestResponse',
                Payload=payload
            )
            print(response['Payload'].read().decode())
            return
    raise ValueError(f"No Lambda function found for service {service_name}")

# Testing Specific Lambda Function (Get-Stock) Change Later
invoke_function_in_namespace("ns-ccodzupqwu4kvz3d", "Get-Stock", json.dumps({
    "httpMethod": "GET",
    "pathParameters": {
        "ticker": "AAPL"
    }
}
))