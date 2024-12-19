import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  // State to store discovered services, user input, and API responses
  const [services, setServices] = useState({});
  const [singleStock, setSingleStock] = useState('');
  const [multipleStocks, setMultipleStocks] = useState('');
  const [stockUpdate, setStockUpdate] = useState('');
  const [newStock, setNewStock] = useState('');
  const [deleteStock, setDeleteStock] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');

  // API Gateway and service discovery configurations
  const apiUrl = 'https://1aelrvkum9.execute-api.us-east-1.amazonaws.com/Prod/stock';
  const namespaceId = 'ns-ccodzupqwu4kvz3d'; // Replace with your namespace ID

  // Discover services dynamically
  useEffect(() => {
    const discoverServices = async () => {
      try {
        const result = await axios.get(`${apiUrl}/discover-services`, {
          params: { namespaceId },
        });

        const discoveredServices = result.data.services.reduce((map, service) => {
          map[service.Name] = service; // Map service names to service objects
          return map;
        }, {});

        setServices(discoveredServices);
        setError('');
      } catch (err) {
        setError('Error discovering services');
        setServices({});
      }
    };

    discoverServices();
  }, []);

  // Mapping service names to API Gateway paths and HTTP methods
  const serviceApiMapping = {
    'Get-Stock': {
      httpMethod: 'GET',
      pathTemplate: '/{ticker}',
    },
    'Update-Stock': {
      httpMethod: 'PUT',
      pathTemplate: '/{ticker}',
    },
    'Get-Stocks': {
      httpMethod: 'GET',
      pathTemplate: '/list',
    },
    'Create-Stock': {
      httpMethod: 'POST',
      pathTemplate: '',
    },
    'Delete-Stock': {
      httpMethod: 'DELETE',
      pathTemplate: '/{ticker}',
    },
  };

  // Generic function to invoke services
  const invokeService = async (serviceName, dynamicParams, payload) => {
    try {
      const serviceInfo = services[serviceName];
      if (!serviceInfo || !serviceApiMapping[serviceName]) {
        throw new Error(`Service ${serviceName} not found or not mapped`);
      }

      const { httpMethod, pathTemplate } = serviceApiMapping[serviceName];
      let path = pathTemplate;

      // Replace dynamic parameters in path
      Object.entries(dynamicParams).forEach(([key, value]) => {
        path = path.replace(`{${key}}`, value);
      });

      const result = await axios.request({
        method: httpMethod,
        url: `${apiUrl}${path}`,
        headers: { 'Content-Type': 'application/json' },
        data: payload || undefined,
        params: httpMethod === 'GET' ? payload : undefined,
      });

      setResponse(result.data);
      setError('');
    } catch (err) {
      setError(`Error invoking ${serviceName}: ${err.message}`);
      setResponse(null);
    }
  };

  return (
    <div>
      <h1>Stock Tracker</h1>
      
      {Object.keys(services).length > 0 ? (
        <>
          {/* Get single stock */}
          <div>
            <h2>Get Single Stock</h2>
            <input
              type="text"
              value={singleStock}
              onChange={(e) => setSingleStock(e.target.value)}
              placeholder="Enter stock symbol"
            />
            <button
              onClick={() => invokeService('Get-Stock', { ticker: singleStock })}
            >
              Get Stock
            </button>
          </div>

          {/* Get multiple stocks */}
          <div>
            <h2>Get Multiple Stocks</h2>
            <input
              type="text"
              value={multipleStocks}
              onChange={(e) => setMultipleStocks(e.target.value)}
              placeholder="Enter stock symbols, comma-separated"
            />
            <button
              onClick={() =>
                invokeService(
                  'Get-Stocks',
                  {},
                  { symbols: multipleStocks.split(',').map((s) => s.trim()) }
                )
              }
            >
              Get Stocks
            </button>
          </div>

          {/* Update stock */}
          <div>
            <h2>Update Stock</h2>
            <input
              type="text"
              value={stockUpdate}
              onChange={(e) => setStockUpdate(e.target.value)}
              placeholder="Enter stock symbol to update"
            />
            <button
              onClick={() =>
                invokeService('Update-Stock', { ticker: stockUpdate }, { price: 155.5 })
              }
            >
              Update Stock
            </button>
          </div>

          {/* Create stock */}
          <div>
            <h2>Create Stock</h2>
            <input
              type="text"
              value={newStock}
              onChange={(e) => setNewStock(e.target.value)}
              placeholder="Enter new stock symbol"
            />
            <button
              onClick={() =>
                invokeService('Create-Stock', {}, { ticker: newStock, price: 100.0 })
              }
            >
              Create Stock
            </button>
          </div>

          {/* Delete stock */}
          <div>
            <h2>Delete Stock</h2>
            <input
              type="text"
              value={deleteStock}
              onChange={(e) => setDeleteStock(e.target.value)}
              placeholder="Enter stock symbol to delete"
            />
            <button
              onClick={() => invokeService('Delete-Stock', { ticker: deleteStock })}
            >
              Delete Stock
            </button>
          </div>
        </>
      ) : (
        <div>Discovering services...</div>
      )}

      {/* Display response or error */}
      <div>
        {response && (
          <div>
            <h3>Response:</h3>
            <pre>{JSON.stringify(response, null, 2)}</pre>
          </div>
        )}
        {error && <div style={{ color: 'red' }}>{error}</div>}
      </div>
    </div>
  );
};

export default App;