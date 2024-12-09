import requests

def get_stock_via_api_gateway(api_endpoint, ticker, headers=None):
    try:
        # Construct the URL with the ticker as a path parameter
        url = f"{api_endpoint}/{ticker}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        raise

# Example Usage
api_gateway_base_url = "https://1aelrvkum9.execute-api.us-east-1.amazonaws.com/Prod/stock"  # Replace with actual endpoint
ticker_symbol = "AAPL"

try:
    result = get_stock_via_api_gateway(api_gateway_base_url, ticker_symbol)
    print("API Gateway Response:", result)
except Exception as e:
    print(f"Error invoking API Gateway: {e}")
