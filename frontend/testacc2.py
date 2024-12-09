import requests
import json

def invoke_lambda_via_api_gateway(api_endpoint, http_method='GET', path='', query_params=None, payload=None, headers=None):
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
        print(f"Constructed URL: {url}")

        # Prepare the request parameters
        request_params = {
            'method': http_method.upper(),
            'url': url,
            'headers': headers or {},
            'params': query_params or {},
            'json': payload if payload else None
        }

        print(f"Request Parameters: {request_params}")

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

# Example Usage
if __name__ == "__main__":
    # Base API Gateway URL (without trailing slash)
    api_gateway_base_url = "https://1aelrvkum9.execute-api.us-east-1.amazonaws.com/Prod"  # Replace with your actual endpoint

    # Example 1: GET request to invoke 'get-stock' Lambda function with path parameter 'AAPL'
    try:
        result_stock = invoke_lambda_via_api_gateway(
            api_endpoint=api_gateway_base_url,
            http_method='GET',
            path='/stock/AAPL',  # Assuming the API expects the ticker as a path parameter
            headers={
                'Content-Type': 'application/json'
                # Add other headers like API keys if required
            }
        )
        print("Get Stock Stock API Gateway Response:", result_stock)
    except Exception as e:
        print(f"Error invoking Stock API Gateway: {e}")

    # Example 2: Run Update-Stock (with TSLA)
    try:
        result_user_create = invoke_lambda_via_api_gateway(
            api_endpoint=api_gateway_base_url,
            http_method='PUT',
            path='/stock/TSLA',
            headers={
                'Content-Type': 'application/json'
                # Add other headers like API keys if required
            }
        )
        print("Update Stock API Response:", result_user_create)
    except Exception as e:
        print(f"Error invoking User Create API Gateway: {e}")

    # Example 3: Run Get-Stocks
    try:
        result_update = invoke_lambda_via_api_gateway(
            api_endpoint=api_gateway_base_url,
            http_method='GET',
            path='/stock/list',
            headers={
                'Content-Type': 'application/json'
                # Add other headers like API keys if required
            }
        )
        print("Get Stocks API Response:", result_update)
    except Exception as e:
        print(f"Error invoking Stock Update API Gateway: {e}")
