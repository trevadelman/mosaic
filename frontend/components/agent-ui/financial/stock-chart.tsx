/**
 * Stock Chart Component
 * 
 * This component displays a stock chart using Recharts.
 * It's a sample implementation of a custom UI component for the Financial Analysis Agent.
 */

"use client"

import React, { useEffect, useRef, useState } from 'react';
import { useAgentUI } from '../../../lib/contexts/agent-ui-context';
import { UIEvent } from '../../../lib/types/agent-ui';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

// Mock data for demonstration purposes
const generateMockData = (days = 30) => {
  const data = [];
  let price = 150;
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  
  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    // Random price movement
    const change = (Math.random() - 0.5) * 5;
    price += change;
    
    // Ensure price doesn't go below 50
    price = Math.max(50, price);
    
    // Generate OHLC data
    const open = price;
    const high = price + Math.random() * 3;
    const low = price - Math.random() * 3;
    const close = price + (Math.random() - 0.5) * 2;
    
    // Generate volume data
    const volume = Math.floor(Math.random() * 1000000) + 500000;
    
    data.push({
      date: date.toISOString().split('T')[0],
      open,
      high,
      low,
      close,
      volume
    });
  }
  
  return data;
};

interface StockChartProps {
  /** The ID of the component */
  componentId: string;
  /** The ID of the agent */
  agentId: string;
  /** The stock symbol */
  symbol?: string;
  /** The title of the chart */
  title?: string;
  /** The description of the chart */
  description?: string;
}

export const StockChart: React.FC<StockChartProps> = ({
  componentId,
  agentId,
  symbol = 'AAPL',
  title = 'Stock Chart',
  description = 'Interactive stock chart'
}) => {
  const { sendUIEvent } = useAgentUI();
  const [data, setData] = useState(generateMockData());
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('1M');
  const [chartType, setChartType] = useState('line');
  const [currentSymbol, setCurrentSymbol] = useState(symbol);
  const chartRef = useRef<HTMLDivElement>(null);
  const loadingRef = useRef(false);
  
  // Keep the ref in sync with the state
  useEffect(() => {
    loadingRef.current = loading;
  }, [loading]);
  
  // Request data from the backend when the component mounts or when symbol/timeRange changes
  useEffect(() => {
    console.log(`StockChart: Requesting data for ${symbol} with range ${timeRange}`);
    
    // Set up an event listener for data responses
    const handleUIEvent = (event: CustomEvent<any>) => {
      const eventData = event.detail;
      console.log('StockChart: Received UI event:', eventData);
      
      // Check if this is a data response for our component
      if (
        eventData.type === 'data_response' && 
        eventData.component === componentId && 
        eventData.action === 'stock_data'
      ) {
        console.log('StockChart: Received stock data:', eventData.data);
        
        // Update the data
        if (eventData.data && eventData.data.data) {
          console.log('StockChart: Setting data:', eventData.data.data);
          setData(eventData.data.data);
          
          // Update the symbol if it's different
          if (eventData.data.symbol && eventData.data.symbol !== currentSymbol) {
            console.log(`StockChart: Updating symbol from ${currentSymbol} to ${eventData.data.symbol}`);
            setCurrentSymbol(eventData.data.symbol);
          }
        }
        
        // Stop loading
        setLoading(false);
      }
    };
    
    // Add event listener
    console.log('StockChart: Adding UI event listener');
    window.addEventListener('ui_event', handleUIEvent as EventListener);
    
    let timeoutId: NodeJS.Timeout | null = null;
    
    try {
      // Send a data request event to the backend
      sendUIEvent({
        type: 'data_request',
        component: componentId,
        action: 'get_stock_data',
        data: {
          symbol,
          range: timeRange
        }
      });
      
      setLoading(true);
      
      // Set a timeout to stop loading after 10 seconds if no response is received
      timeoutId = setTimeout(() => {
        console.log('Timeout reached, checking if still loading');
        // Use a ref to check the current loading state
        if (loadingRef.current) {
          console.log('Still loading after timeout, falling back to mock data');
          setData(generateMockData());
          setLoading(false);
        } else {
          console.log('No longer loading, data was received before timeout');
        }
      }, 10000); // Increased to 10 seconds
    } catch (error) {
      console.error('Error sending UI event:', error);
      
      // Fall back to mock data if there's an error
      console.log('Falling back to mock data');
      setData(generateMockData());
      setLoading(false);
    }
    
    // Clean up
    return () => {
      console.log('Cleaning up: removing event listener and clearing timeout');
      window.removeEventListener('ui_event', handleUIEvent as EventListener);
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [componentId, symbol, timeRange, sendUIEvent]);
  
  // Handle time range change
  const handleTimeRangeChange = (range: string) => {
    setTimeRange(range);
    setLoading(true);
    
    try {
      // Send a data request event to the backend with the new range
      sendUIEvent({
        type: 'user_action',
        component: componentId,
        action: 'change_range',
        data: {
          symbol: currentSymbol,
          range
        }
      });
      
      console.log(`StockChart: Requested data for ${currentSymbol} with new range ${range}`);
      
      // Set a timeout to stop loading after 10 seconds if no response is received
      setTimeout(() => {
        console.log('Timeout check for time range change');
        // Need to check the current state since it might have changed
        if (loadingRef.current) {
          console.log('Timeout reached for time range change, falling back to mock data');
          
          // Generate new mock data based on the range
          let days = 30;
          switch (range) {
            case '1D':
              days = 1;
              break;
            case '1W':
              days = 7;
              break;
            case '1M':
              days = 30;
              break;
            case '3M':
              days = 90;
              break;
            case '1Y':
              days = 365;
              break;
            case '5Y':
              days = 365 * 5;
              break;
          }
          
          setData(generateMockData(days));
          setLoading(false);
        } else {
          console.log('No longer loading for time range change, data was received');
        }
      }, 10000); // Increased to 10 seconds
    } catch (error) {
      console.error('Error sending UI event:', error);
      
      // Fall back to mock data if there's an error
      console.log('Falling back to mock data for time range change');
      
      // Generate new mock data based on the range
      let days = 30;
      switch (range) {
        case '1D':
          days = 1;
          break;
        case '1W':
          days = 7;
          break;
        case '1M':
          days = 30;
          break;
        case '3M':
          days = 90;
          break;
        case '1Y':
          days = 365;
          break;
        case '5Y':
          days = 365 * 5;
          break;
      }
      
      setData(generateMockData(days));
      setLoading(false);
    }
  };
  
  // Handle chart type change
  const handleChartTypeChange = (type: string) => {
    setChartType(type);
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Chart header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div>
          <h3 className="text-lg font-semibold">{currentSymbol} - {title}</h3>
          <p className="text-sm text-muted-foreground">{description}</p>
          
          {/* Symbol search */}
          <div className="mt-2 flex items-center">
            <input
              type="text"
              placeholder="Enter stock symbol"
              className="px-2 py-1 text-sm border rounded mr-2 w-32"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const newSymbol = e.currentTarget.value.toUpperCase();
                  if (newSymbol && newSymbol !== currentSymbol) {
                    try {
                      // Send a data request event to the backend with the new symbol
                      sendUIEvent({
                        type: 'user_action',
                        component: componentId,
                        action: 'change_symbol',
                        data: {
                          symbol: newSymbol,
                          range: timeRange
                        }
                      });
                      
                      // Update the symbol
                      setCurrentSymbol(newSymbol);
                      setLoading(true);
                      console.log(`StockChart: Requested data for new symbol ${newSymbol}`);
                      
                      // Set a timeout to stop loading after 10 seconds if no response is received
                      setTimeout(() => {
                        console.log('Timeout check for symbol change');
                        // Need to check the current state since it might have changed
                        if (loadingRef.current) {
                          console.log('Timeout reached for symbol change, falling back to mock data');
                          setData(generateMockData());
                          setLoading(false);
                        } else {
                          console.log('No longer loading for symbol change, data was received');
                        }
                      }, 10000); // Increased to 10 seconds
                    } catch (error) {
                      console.error('Error sending UI event:', error);
                      
                      // Fall back to mock data if there's an error
                      console.log('Falling back to mock data for symbol change');
                      setCurrentSymbol(newSymbol);
                      setData(generateMockData());
                      setLoading(false);
                    }
                  }
                }
              }}
            />
            <span className="text-xs text-muted-foreground">Press Enter to search</span>
          </div>
        </div>
        
        {/* Chart controls */}
        <div className="flex items-center gap-4">
          {/* Time range selector */}
          <div className="flex items-center gap-1">
            {['1D', '1W', '1M', '3M', '1Y', '5Y'].map((range) => (
              <button
                key={range}
                className={`px-2 py-1 text-xs rounded ${
                  timeRange === range
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                }`}
                onClick={() => handleTimeRangeChange(range)}
              >
                {range}
              </button>
            ))}
          </div>
          
          {/* Chart type selector */}
          <div className="flex items-center gap-1">
            {['line', 'candle', 'bar'].map((type) => (
              <button
                key={type}
                className={`px-2 py-1 text-xs rounded ${
                  chartType === type
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                }`}
                onClick={() => handleChartTypeChange(type)}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {/* Chart content */}
      <div className="flex-1 p-4">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="h-full" ref={chartRef}>
            {/* This is a placeholder for the actual chart */}
            {/* In a real implementation, we would use D3.js or a charting library */}
            <div className="flex flex-col h-full border rounded-lg p-4">
              <div className="text-center mb-4">
                <h4 className="text-lg font-semibold">{currentSymbol} Stock Chart</h4>
                <p className="text-sm text-muted-foreground">
                  {chartType.charAt(0).toUpperCase() + chartType.slice(1)} chart for {timeRange} time range
                </p>
              </div>
              
              <div className="flex-1">
                {data.length > 0 ? (
                  <div className="w-full h-full">
                    <ResponsiveContainer width="100%" height="100%">
                      {chartType === 'line' ? (
                        <LineChart data={data}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis domain={['auto', 'auto']} />
                          <Tooltip />
                          <Legend />
                          <Line type="monotone" dataKey="close" stroke="#8884d8" name="Close Price" />
                          <Line type="monotone" dataKey="open" stroke="#82ca9d" name="Open Price" />
                        </LineChart>
                      ) : chartType === 'bar' ? (
                        <BarChart data={data}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis domain={['auto', 'auto']} />
                          <Tooltip />
                          <Legend />
                          <Bar dataKey="volume" fill="#8884d8" name="Volume" />
                        </BarChart>
                      ) : (
                        <AreaChart data={data}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis domain={['auto', 'auto']} />
                          <Tooltip />
                          <Legend />
                          <Area type="monotone" dataKey="high" stroke="#8884d8" fill="#8884d8" name="High" />
                          <Area type="monotone" dataKey="low" stroke="#82ca9d" fill="#82ca9d" name="Low" />
                        </AreaChart>
                      )}
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-muted-foreground">
                      No data available for {currentSymbol} with {timeRange} time range.
                    </p>
                  </div>
                )}
              </div>
              
              <div className="mt-4">
                <h5 className="text-sm font-semibold mb-2">Data Preview:</h5>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Date</th>
                        <th className="text-right p-2">Open</th>
                        <th className="text-right p-2">High</th>
                        <th className="text-right p-2">Low</th>
                        <th className="text-right p-2">Close</th>
                        <th className="text-right p-2">Volume</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.slice(0, 5).map((item, index) => (
                        <tr key={index} className="border-b">
                          <td className="text-left p-2">{item.date}</td>
                          <td className="text-right p-2">{item.open.toFixed(2)}</td>
                          <td className="text-right p-2">{item.high.toFixed(2)}</td>
                          <td className="text-right p-2">{item.low.toFixed(2)}</td>
                          <td className="text-right p-2">{item.close.toFixed(2)}</td>
                          <td className="text-right p-2">{item.volume.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
