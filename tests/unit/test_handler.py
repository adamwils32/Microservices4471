# tests/unit/test_handler.py

import json
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
import uuid

# Sample test data
TEST_STOCK_AAPL = {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "exchange": "NASDAQ",
    "sector": "Technology"
}

TEST_STOCK_TSLA = {
    "ticker": "TSLA",
    "company_name": "Tesla, Inc.",
    "exchange": "NASDAQ",
    "sector": "Automotive"
}

@pytest.fixture()
def apigw_event_create():
    """Generates API GW Event for create_stock"""
    return {
        "body": json.dumps(TEST_STOCK_AAPL),
        "resource": "/stock",
        "httpMethod": "POST",
        "path": "/stock",
        "headers": {
            "Content-Type": "application/json"
        }
    }

@pytest.fixture()
def apigw_event_get():
    """Generates API GW Event for get_stock"""
    return {
        "pathParameters": {"ticker": "AAPL"},
        "resource": "/stock/{ticker}",
        "httpMethod": "GET",
        "path": "/stock/AAPL",
        "headers": {
            "Content-Type": "application/json"
        }
    }

@pytest.fixture()
def apigw_event_update():
    """Generates API GW Event for update_stock"""
    return {
        "pathParameters": {"ticker": "AAPL"},
        "resource": "/stock/{ticker}",
        "httpMethod": "PUT",
        "path": "/stock/AAPL",
        "headers": {
            "Content-Type": "application/json"
        }
    }

@pytest.fixture()
def apigw_event_delete():
    """Generates API GW Event for delete_stock"""
    return {
        "pathParameters": {"ticker": "AAPL"},
        "resource": "/stock/{ticker}",
        "httpMethod": "DELETE",
        "path": "/stock/AAPL",
        "headers": {
            "Content-Type": "application/json"
        }
    }

@pytest.fixture()
def apigw_event_compare():
    """Generates API GW Event for compare_stocks"""
    return {
        "queryStringParameters": {
            "ticker1": "AAPL",
            "ticker2": "TSLA"
        },
        "resource": "/stock/compare",
        "httpMethod": "GET",
        "path": "/stock/compare",
        "headers": {
            "Content-Type": "application/json"
        }
    }

@pytest.fixture()
def apigw_event_get_stocks():
    """Generates API GW Event for get_stocks"""
    return {
        "resource": "/stock/list",
        "httpMethod": "GET",
        "path": "/stock/list",
        "headers": {
            "Content-Type": "application/json"
        }
    }

# -------------------------------
# Test for create_stock Handler
# -------------------------------

@patch('create_stock.app.boto3.resource')
def test_create_stock(mock_boto3_resource, apigw_event_create):
    """
    Test the create_stock_handler by adding a new stock.
    """
    # Import the handler **after** mocking boto3.resource
    from create_stock.app import lambda_handler as create_stock_handler

    # Mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table

    # Mock put_item response
    mock_table.put_item.return_value = {}

    # Call the handler
    response = create_stock_handler(apigw_event_create, None)

    # Assertions
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "message" in body
    assert body["message"] == "A new stock was saved successfully in the database"

    # Ensure put_item was called once
    mock_table.put_item.assert_called_once()

    # Retrieve the actual call arguments
    called_args, called_kwargs = mock_table.put_item.call_args

    # Define expected key-value pairs
    expected_item = TEST_STOCK_AAPL

    # Verify expected fields are present
    for key, value in expected_item.items():
        assert key in called_kwargs['Item'], f"Missing key: {key}"
        assert called_kwargs['Item'][key] == value, f"Incorrect value for key {key}: expected {value}, got {called_kwargs['Item'][key]}"

    # Verify 'id' field exists
    assert 'id' in called_kwargs['Item'], "Missing 'id' field in Item"

    # Optionally, verify 'id' is a valid UUID
    try:
        uuid_obj = uuid.UUID(called_kwargs['Item']['id'], version=4)
    except ValueError:
        pytest.fail(f"'id' field is not a valid UUID: {called_kwargs['Item']['id']}")

# -------------------------------
# Test for get_stock Handler
# -------------------------------

@patch('get_stock.app.boto3.resource')
def test_get_stock(mock_boto3_resource, apigw_event_get):
    """
    Test the get_stock_handler for retrieving a stock.
    """
    # Import the handler
    from get_stock.app import lambda_handler as get_stock_handler

    # Mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table

    # Mock get_item response
    mock_table.get_item.return_value = {
        "Item": TEST_STOCK_AAPL
    }

    # Call the handler
    response = get_stock_handler(apigw_event_get, None)

    # Assertions
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["ticker"] == "AAPL"
    assert body["company_name"] == "Apple Inc."
    assert body["exchange"] == "NASDAQ"
    assert body["sector"] == "Technology"
    # 'price' and 'volume' should not be present
    assert "price" not in body
    assert "volume" not in body

    # Ensure get_item was called with correct parameters
    mock_table.get_item.assert_called_with(Key={"ticker": "AAPL"})

# -------------------------------
# Test for update_stock Handler
# -------------------------------

@patch.dict('update_stock.app.os.environ', {'ALPHA_VANTAGE_API_KEY': 'RYXS7QBFIK5870FS'})  # Insert Alpha Vantage API Key Here (only used for tests)
@patch('update_stock.app.boto3.resource')
@patch('update_stock.app.urllib.request.urlopen')
def test_update_stock(mock_urlopen, mock_boto3_resource, apigw_event_update):
    """
    Test the update_stock_handler by updating a stock's price and volume.
    """
    # Import the handler **after** environment variables and mocks are set
    from update_stock.app import lambda_handler as update_stock_handler

    # Mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table

    # Mock HTTP response from Alpha Vantage API
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = json.dumps({
        "Global Quote": {
            "05. price": "150.00",
            "06. volume": "1000000"
        }
    }).encode('utf-8')  # Mocked response needs to be bytes

    mock_urlopen.return_value = mock_response

    # Call the handler
    response = update_stock_handler(apigw_event_update, None)

    # Assertions
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "message" in body
    assert body["message"] == "Stock data was updated successfully in the database"

    # Ensure urllib.request.urlopen was called with correct URL
    mock_urlopen.assert_called_once()
    called_url = mock_urlopen.call_args[0][0]
    assert "https://www.alphavantage.co/query" in called_url
    assert "symbol=AAPL" in called_url

    # Ensure update_item was called with correct parameters
    mock_table.update_item.assert_called_with(
        Key={"ticker": "AAPL"},
        UpdateExpression="set price=:p, volume=:v",
        ExpressionAttributeValues={
            ":p": Decimal('150.00'),
            ":v": Decimal('1000000')
        },
        ReturnValues="UPDATED_NEW"
    )

# -------------------------------
# Test for delete_stock Handler
# -------------------------------

@patch('delete_stock.app.boto3.resource')
def test_delete_stock(mock_boto3_resource, apigw_event_delete):
    """
    Test the delete_stock_handler by deleting a stock.
    """
    # Import the handler
    from delete_stock.app import lambda_handler as delete_stock_handler

    # Mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table

    # Mock delete_item response
    mock_table.delete_item.return_value = {}

    # Call the handler
    response = delete_stock_handler(apigw_event_delete, None)

    # Assertions
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "message" in body
    assert body["message"] == "The stock was deleted successfully from the database"

    # Ensure delete_item was called with correct parameters
    mock_table.delete_item.assert_called_with(
        Key={"ticker": "AAPL"},
        ConditionExpression="attribute_exists(ticker)"
    )

# -------------------------------
# Test for compare_stocks Handler
# -------------------------------

@patch.dict('compare_stocks.app.os.environ', {'ALPHA_VANTAGE_API_KEY': 'RYXS7QBFIK5870FS'})  # Insert API Key
@patch('compare_stocks.app.boto3.resource')
@patch('compare_stocks.app.urllib.request.urlopen')
def test_compare_stocks(mock_urlopen, mock_boto3_resource, apigw_event_compare):
    """
    Test the compare_stocks_handler by comparing two stocks.
    """
    # Import the handler
    from compare_stocks.app import lambda_handler as compare_stocks_handler

    # Mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table

    # Mock get_item responses for both stocks
    mock_table.get_item.side_effect = [
        {"Item": TEST_STOCK_AAPL},
        {"Item": TEST_STOCK_TSLA}
    ]

    # Mock Alpha Vantage API responses for both stocks
    mock_response_aapl = MagicMock()
    mock_response_aapl.status = 200
    mock_response_aapl.read.return_value = json.dumps({
        "Global Quote": {
            "05. price": "150.00",
            "06. volume": "1000000"
        }
    }).encode('utf-8')

    mock_response_tsla = MagicMock()
    mock_response_tsla.status = 200
    mock_response_tsla.read.return_value = json.dumps({
        "Global Quote": {
            "05. price": "800.00",
            "06. volume": "2500000"
        }
    }).encode('utf-8')

    # Define side_effect function to return different responses based on URL
    def side_effect(url, *args, **kwargs):
        if "symbol=AAPL" in url:
            return mock_response_aapl
        elif "symbol=TSLA" in url:
            return mock_response_tsla
        else:
            raise ValueError("Unexpected symbol in URL")

    mock_urlopen.side_effect = side_effect

    # Call the handler
    response = compare_stocks_handler(apigw_event_compare, None)

    # Assertions
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "stock1" in body
    assert "stock2" in body
    assert "comparisons" in body

    # Verify comparison logic
    stock1 = body["stock1"]
    stock2 = body["stock2"]
    comparisons = body["comparisons"]

    assert stock1["ticker"] == "AAPL"
    assert stock2["ticker"] == "TSLA"
    assert comparisons["price_comparison"] == "TSLA has a higher price than AAPL"
    assert comparisons["volume_comparison"] == "TSLA has a higher volume than AAPL"

    # Ensure urllib.request.urlopen was called twice for both stocks
    assert mock_urlopen.call_count == 2

# -------------------------------
# Test for get_stocks Handler
# -------------------------------

@patch('get_stocks.app.boto3.resource')
def test_get_stocks(mock_boto3_resource, apigw_event_get_stocks):
    """
    Test the get_stocks_handler to retrieve all stocks.
    """
    # Import the handler
    from get_stocks.app import lambda_handler as get_stocks_handler

    # Mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table

    # Mock scan response
    mock_table.scan.return_value = {
        "Items": [TEST_STOCK_AAPL, TEST_STOCK_TSLA]
    }

    # Call the handler
    response = get_stocks_handler(apigw_event_get_stocks, None)

    # Assertions
    assert response["statusCode"] == 200
    stocks = json.loads(response["body"])
    assert isinstance(stocks, list)
    assert len(stocks) == 2
    assert TEST_STOCK_AAPL in stocks
    assert TEST_STOCK_TSLA in stocks

    # Ensure scan was called
    mock_table.scan.assert_called_once()