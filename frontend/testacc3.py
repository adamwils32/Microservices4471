import boto3
import json
import requests


def discover_services(namespace_id, service_names=None):
    """
    Discovers services in a given namespace using AWS Cloud Map.

    :param namespace_id: The ID of the namespace to search within.
    :param service_names: Optional list of service names to filter.
    :return: List of discovered services with their attributes.
    """
    client = boto3.client('servicediscovery', region_name='us-east-1')

    try:
        # List all services in the namespace
        services_response = client.list_services(
            Filters=[{'Name': 'NAMESPACE_ID', 'Values': [namespace_id]}]
        )
        services = services_response.get('Services', [])


        if service_names:
            # Filter services by the provided service names
            services = [s for s in services if s['Name'] in service_names]

        if not services:
            print(f"No services found in namespace '{namespace_id}' with the specified criteria.")
            return []

        print(f"Discovered {len(services)} service(s) in namespace '{namespace_id}'.")
        for service in services:
            print(f" - Service Name: {service['Name']}, Service ID: {service['Id']}")

        return services

    except Exception as e:
        print(f"Error discovering services: {e}")
        raise


def invoke_lambda_via_api_gateway(api_endpoint, http_method='GET', path='', query_params=None, payload=None,
                                  headers=None):
    """
    Invokes a Lambda function through API Gateway.

    :param api_endpoint: The base URL of the API Gateway (e.g., https://abc123.execute-api.us-east-1.amazonaws.com/Prod)
    :param http_method: HTTP method to use (GET, POST, PUT, DELETE, etc.)
    :param path: The specific resource path (e.g., '/stock', '/user/create')
    :param query_params: Dictionary of query parameters (e.g., {'ticker': 'AAPL'})
    :param payload: Dictionary representing the JSON payload to send in the body (for POST, PUT, etc.)
    :param headers: Dictionary of HTTP headers to include in the request
    :return: The JSON response from the API Gateway
    """
    try:
        # Construct the full URL
        url = f"{api_endpoint.rstrip('/')}/{path.lstrip('/')}"  # Ensure no double slashes
        print(f"\nConstructed URL: {url}")

        # Prepare the request parameters
        request_params = {
            'method': http_method.upper(),
            'url': url,
            'headers': headers or {},
            'params': query_params or {},
            'json': payload if payload else None
        }

        print(f"Request Parameters: {json.dumps(request_params, indent=4)}")

        # Make the HTTP request
        response = requests.request(**request_params)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

        # Attempt to parse JSON response
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Response is not in JSON format.")
            return response.text

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response Content: {response.text}")
        raise
    except requests.exceptions.RequestException as req_err:
        print(f"Request exception occurred: {req_err}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def main():
    # Configuration
    namespace_id = "ns-ccodzupqwu4kvz3d"  # Replace with your actual namespace ID
    api_gateway_base_url = "https://1aelrvkum9.execute-api.us-east-1.amazonaws.com/Prod"  # Replace with your actual API Gateway base URL

    # Define the services you want to discover and invoke
    services_to_invoke = ["Get-Stock", "Update-Stock", "Get-Stocks"]

    # Mapping from service names to API Gateway paths and HTTP methods
    service_api_mapping = {
        "Get-Stock": {
            "http_method": "GET",
            "path_template": "/stock/{ticker}"
        },
        "Update-Stock": {
            "http_method": "PUT",
            "path_template": "/stock/{ticker}"
        },
        "Get-Stocks": {
            "http_method": "GET",
            "path_template": "/stock/list"
        },
        "Delete-Stock": {
            "http_method": "DELETE",
            "path_template": "/stock/{ticker}"
        },
        "Compare-Stocks": {
            "http_method": "GET",
            "path_template": "/stock/compare"
        },
        "Create-Stock": {
            "http_method": "POST",
            "path_template": "/stock"
        }

        # Add more mappings as needed
    }

    # Step 1: Discover services via Service Discovery
    services = discover_services(namespace_id, service_names=services_to_invoke)

    # Step 2: Invoke each service via API Gateway
    for service in services:
        service_name = service['Name']
        if service_name not in service_api_mapping:
            print(f"Service '{service_name}' is not mapped to an API Gateway endpoint. Skipping.")
            continue

        api_info = service_api_mapping[service_name]
        http_method = api_info['http_method']
        path_template = api_info['path_template']

        # Prepare dynamic path parameters if needed
        if "{ticker}" in path_template:
            # Example: Provide the ticker symbol based on service
            if service_name == "Get-Stock":
                ticker = "AAPL"
            elif service_name == "Update-Stock":
                ticker = "TSLA"
            else:
                ticker = "UNKNOWN"

            path = path_template.replace("{ticker}", ticker)
        else:
            path = path_template

        # Prepare payload based on service and HTTP method
        if service_name == "Get-Stock" and http_method == "GET":
            # Typically, GET requests do not have a payload
            payload = None
        elif service_name == "Update-Stock" and http_method == "PUT":
            payload = {
                "price": 155.50  # Example payload for updating stock price
            }
        elif service_name == "Get-Stocks" and http_method == "GET":
            payload = None
        elif service_name == "Compare-Stocks":
            query_params = {
                'ticker1': 'AAPL',
                'ticker2': 'TSLA'
            }
        else:
            payload = {
                # Define payload based on service requirements
            }

        # Define headers, including API keys if required
        headers = {
            'Content-Type': 'application/json'
            # 'x-api-key': 'YOUR_API_KEY'  # Uncomment and set if API keys are required
        }

        # Invoke the service via API Gateway
        try:
            print(f"\nInvoking service '{service_name}' via API Gateway...")
            response = invoke_lambda_via_api_gateway(
                api_endpoint=api_gateway_base_url,
                http_method=http_method,
                path=path,
                query_params=query_params,
                payload=payload,
                headers=headers
            )
            print(f"API Gateway Response for '{service_name}': {json.dumps(response, indent=4)}")
        except Exception as e:
            print(f"Error invoking service '{service_name}' via API Gateway: {e}")


if __name__ == "__main__":
    main()
