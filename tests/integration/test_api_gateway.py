import json
import unittest
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAPIGateway(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load configuration from config.json
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path) as config_file:
            config = json.load(config_file)

        # API Gateway Configuration
        cls.base_url = config['api_gateway']['base_url']
        cls.endpoints = config['api_gateway']['endpoints']

        # Load headers, including API key from environment variable if present
        cls.api_key = os.getenv('API_KEY')
        cls.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if cls.api_key:
            cls.headers['x-api-key'] = cls.api_key
            logger.info("API Key loaded from environment variables.")
        else:
            logger.info("No API Key found in environment variables.")

        # Test Data
        cls.test_stock_aapl = {
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "exchange": "NASDAQ",
            "sector": "Technology"
        }
        cls.test_stock_tsla = {
            "ticker": "TSLA",
            "company_name": "Tesla, Inc.",
            "exchange": "NASDAQ",
            "sector": "Automotive"
        }

    def test_1_create_stock_aapl(self):
        """
        Test the create_stock service by adding a new stock (AAPL) to the database.
        """
        url = f"{self.base_url}{self.endpoints['create_stock']}"
        logger.info(f"Creating stock AAPL at {url}")
        response = requests.post(url, headers=self.headers, json=self.test_stock_aapl)
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        response_body = response.json()
        self.assertIn('message', response_body)
        self.assertEqual(response_body['message'], 'A new stock was saved successfully in the database')

    def test_2_create_stock_tsla(self):
        """
        Test the create_stock service by adding a new stock (TSLA).
        """
        url = f"{self.base_url}{self.endpoints['create_stock']}"
        logger.info(f"Creating stock TSLA at {url}")
        response = requests.post(url, headers=self.headers, json=self.test_stock_tsla)
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        response_body = response.json()
        self.assertIn('message', response_body)
        self.assertEqual(response_body['message'], 'A new stock was saved successfully in the database')

    def test_3_get_stock_aapl(self):
        """
        Test the get_stock service for AAPL.
        """
        ticker = "AAPL"
        url = f"{self.base_url}{self.endpoints['get_stock']}".replace("{ticker}", ticker)
        logger.info(f"Retrieving stock AAPL from {url}")
        response = requests.get(url, headers=self.headers)
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        stock = response.json()
        self.assertEqual(stock['ticker'], ticker)
        # Remove assertions for 'price' and 'volume' as they are not set yet
        # self.assertIn('price', stock)
        # self.assertIn('volume', stock)
        # Instead, check for other attributes
        self.assertIn('company_name', stock)
        self.assertIn('exchange', stock)
        self.assertIn('sector', stock)

    def test_4_get_stock_tsla(self):
        """
        Test the get_stock service for TSLA.
        """
        ticker = "TSLA"
        url = f"{self.base_url}{self.endpoints['get_stock']}".replace("{ticker}", ticker)
        logger.info(f"Retrieving stock TSLA from {url}")
        response = requests.get(url, headers=self.headers)
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        stock = response.json()
        self.assertEqual(stock['ticker'], ticker)
        # Remove assertions for 'price' and 'volume' as they are not set yet
        # self.assertIn('price', stock)
        # self.assertIn('volume', stock)
        # Instead, check for other attributes
        self.assertIn('company_name', stock)
        self.assertIn('exchange', stock)
        self.assertIn('sector', stock)

    def test_5_update_stock_aapl(self):
        """
        Test the update_stock service for AAPL.
        """
        ticker = "AAPL"
        url = f"{self.base_url}{self.endpoints['update_stock']}".replace("{ticker}", ticker)
        logger.info(f"Updating stock AAPL at {url}")
        response = requests.put(url, headers=self.headers)
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        response_body = response.json()
        self.assertIn('message', response_body)
        self.assertEqual(response_body['message'], 'Stock data was updated successfully in the database')

    def test_6_update_stock_tsla(self):
        """
        Test the update_stock service for TSLA.
        """
        ticker = "TSLA"
        url = f"{self.base_url}{self.endpoints['update_stock']}".replace("{ticker}", ticker)
        logger.info(f"Updating stock TSLA at {url}")
        response = requests.put(url, headers=self.headers)
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        response_body = response.json()
        self.assertIn('message', response_body)
        self.assertEqual(response_body['message'], 'Stock data was updated successfully in the database')

    def test_7_compare_stocks_aapl_tsla(self):
        """
        Test the compare_stocks service between AAPL and TSLA.
        """
        url = f"{self.base_url}{self.endpoints['compare_stocks']}"
        params = {
            "ticker1": "AAPL",
            "ticker2": "TSLA"
        }
        logger.info(f"Comparing stocks AAPL and TSLA at {url} with params {params}")
        response = requests.get(url, headers=self.headers, params=params)
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        comparison = response.json()
        self.assertIn('stock1', comparison)
        self.assertIn('stock2', comparison)
        self.assertIn('comparisons', comparison)
        # Additional assertions can be added based on the expected comparison structure

    def test_8_get_stocks(self):
        """
        Test the get_stocks service to retrieve all stocks.
        """
        url = f"{self.base_url}{self.endpoints['get_stocks']}"
        logger.info(f"Retrieving all stocks from {url}")
        response = requests.get(url, headers=self.headers)
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        stocks = response.json()
        self.assertIsInstance(stocks, list)
        self.assertGreaterEqual(len(stocks), 2, "Expected at least two stocks in the list")
        # Verify that both AAPL and TSLA are present
        tickers = [stock['ticker'] for stock in stocks]
        self.assertIn("AAPL", tickers)
        self.assertIn("TSLA", tickers)

    def test_9_delete_stock_tsla(self):
        """
        Test the delete_stock service by deleting TSLA.
        """
        ticker = "TSLA"
        url = f"{self.base_url}{self.endpoints['delete_stock']}".replace("{ticker}", ticker)
        logger.info(f"Deleting stock TSLA at {url}")
        response = requests.delete(url, headers=self.headers)
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        response_body = response.json()
        self.assertIn('message', response_body)
        self.assertEqual(response_body['message'], f'The stock was deleted successfully from the database')

    def test_10_get_stock_tsla_not_found(self):
        """
        Test the get_stock service for TSLA after deletion to ensure it's not found.
        """
        ticker = "TSLA"
        url = f"{self.base_url}{self.endpoints['get_stock']}".replace("{ticker}", ticker)
        logger.info(f"Retrieving deleted stock TSLA from {url}")
        response = requests.get(url, headers=self.headers)
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        self.assertEqual(response.status_code, 404, f"Expected 404, got {response.status_code}")
        response_body = response.json()
        self.assertIn('message', response_body)
        self.assertEqual(response_body['message'], 'Stock not found')

    @classmethod
    def tearDownClass(cls):
        """
        Clean up resources after tests if necessary.
        """
        # Optionally, delete the created AAPL stock to reset state
        url = f"{cls.base_url}{cls.endpoints['delete_stock']}".replace("{ticker}", "AAPL")
        logger.info(f"Cleaning up by deleting stock AAPL at {url}")
        response = requests.delete(url, headers=cls.headers)
        if response.status_code == 200:
            logger.info("Cleanup successful: AAPL deleted.")
        elif response.status_code == 404:
            logger.info("Cleanup: AAPL was already deleted.")
        else:
            logger.warning(f"Cleanup failed with status code {response.status_code}: {response.text}")


if __name__ == '__main__':
    unittest.main()