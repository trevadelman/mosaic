"use client"

import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart, Bar,
  LineChart, Line,
  PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';
import { useAgentUI } from '../../../lib/contexts/agent-ui-context';

// Define props interface
interface ChartVisualizerProps {
  componentId: string;
  agentId: string;
  sendUIEvent: (event: any) => void;
}

// Define chart data interfaces
interface BarChartData {
  type: 'bar';
  categories: string[];
  values: number[];
  colors: string[];
}

interface LineChartData {
  type: 'line';
  dates: string[];
  series: {
    name: string;
    values: number[];
    color: string;
  }[];
}

interface PieChartData {
  type: 'pie';
  segments: string[];
  values: number[];
  colors: string[];
}

type ChartData = BarChartData | LineChartData | PieChartData;

export const ChartVisualizer: React.FC<ChartVisualizerProps> = ({
  componentId,
  agentId,
  sendUIEvent,
}) => {
  // State for chart type and parameters
  const [chartType, setChartType] = useState<'bar' | 'line' | 'pie'>('bar');
  const [numItems, setNumItems] = useState<number>(5);
  const [minValue, setMinValue] = useState<number>(0);
  const [maxValue, setMaxValue] = useState<number>(500);
  const [numSeries, setNumSeries] = useState<number>(3);
  
  // State for chart data
  const [chartData, setChartData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Generate random data based on parameters (fallback for when backend fails)
  const generateRandomData = () => {
    // Generate random bar chart data in the format expected by the component
    const barData = {
      type: 'bar',
      categories: Array.from({ length: numItems }, (_, i) => `Category ${String.fromCharCode(65 + i)}`),
      values: Array.from({ length: numItems }, () => Math.floor(Math.random() * (maxValue - minValue + 1)) + minValue),
      colors: Array.from({ length: numItems }, () => `hsl(${Math.floor(Math.random() * 360)}, 70%, 50%)`)
    };
    
    // Generate random line chart data in the format expected by the component
    const lineData = {
      type: 'line',
      dates: Array.from({ length: numItems }, (_, i) => `Day ${i + 1}`),
      series: Array.from({ length: numSeries }, (_, i) => ({
        name: `Series ${i + 1}`,
        values: Array.from({ length: numItems }, () => Math.floor(Math.random() * (maxValue - minValue + 1)) + minValue),
        color: `hsl(${Math.floor(Math.random() * 360)}, 70%, 50%)`
      }))
    };
    
    // Generate random pie chart data in the format expected by the component
    const pieData = {
      type: 'pie',
      segments: Array.from({ length: numItems }, (_, i) => `Group ${String.fromCharCode(65 + i)}`),
      values: Array.from({ length: numItems }, () => Math.floor(Math.random() * (maxValue - minValue + 1)) + minValue),
      colors: Array.from({ length: numItems }, () => `hsl(${Math.floor(Math.random() * 360)}, 70%, 50%)`)
    };
    
    return { barData, lineData, pieData };
  };
  
  // Function to fetch chart data from the backend
  const fetchChartData = useCallback(() => {
    setLoading(true);
    setError(null);
    
    try {
      // Prepare parameters based on chart type
      let params: any = {
        chart_type: chartType
      };
      
      if (chartType === 'bar') {
        params = {
          ...params,
          num_categories: numItems,
          min_value: minValue,
          max_value: maxValue
        };
      } else if (chartType === 'line') {
        params = {
          ...params,
          points: numItems,
          min_value: minValue,
          max_value: maxValue,
          num_series: numSeries
        };
      } else if (chartType === 'pie') {
        params = {
          ...params,
          num_segments: numItems,
          min_value: minValue,
          max_value: maxValue
        };
      }
      
      // Send request to backend
      console.log('Sending chart data request:', params);
      sendUIEvent({
        type: 'data_request',
        component: componentId,
        action: 'get_chart_data',
        data: params,
        requestId: Date.now().toString()
      });
      
      // Set a timeout for fallback
      const timeoutId = setTimeout(() => {
        if (loading) {
          console.log('Backend request timed out, using client-side data generation');
          console.log('This may happen if the WebSocket connection is not properly forwarding responses');
          console.log('Check the backend logs to see if the data was generated successfully');
          
          const { barData, lineData, pieData } = generateRandomData();
          setChartData(chartType === 'bar' ? barData : chartType === 'line' ? lineData : pieData);
          setLoading(false);
        }
      }, 10000); // 10 second timeout
      
      return () => clearTimeout(timeoutId);
    } catch (err) {
      console.error('Error requesting data from backend:', err);
      const { barData, lineData, pieData } = generateRandomData();
      setChartData(chartType === 'bar' ? barData : chartType === 'line' ? lineData : pieData);
      setLoading(false);
    }
  }, [chartType, numItems, minValue, maxValue, numSeries, componentId, sendUIEvent]);
  
  // Effect to set up event listener for responses
  useEffect(() => {
    // Set up event listener for responses
    const handleUIEvent = (event: CustomEvent<any>) => {
      const data = event.detail;
      
      // Log all UI events for debugging
      console.log('UI event received:', data);
      
      // Check if this event is for our component
      if (data.component === componentId && data.action === 'get_chart_data') {
        console.log('Received chart data response for our component:', data);
        
        if (data.success) {
          console.log('Chart data received successfully:', data.chart_data);
          setChartData(data.chart_data);
        } else {
          console.error('Error getting chart data:', data.error);
          setError(data.error || 'Failed to get chart data');
          // Fallback to client-side data generation
          const { barData, lineData, pieData } = generateRandomData();
          setChartData(chartType === 'bar' ? barData : chartType === 'line' ? lineData : pieData);
        }
        
        setLoading(false);
      }
    };
    
    // Add event listener
    window.addEventListener('ui_event', handleUIEvent as EventListener);
    
    // Clean up
    return () => {
      window.removeEventListener('ui_event', handleUIEvent as EventListener);
    };
  }, [componentId, chartType]);
  
  // Effect to fetch data when component mounts or parameters change
  useEffect(() => {
    fetchChartData();
  }, [fetchChartData]);
  
  // Chart dimensions
  const chartWidth = 500;
  const chartHeight = 300;
  
  // Render the appropriate chart based on the selected type
  const renderChart = () => {
    if (!chartData) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="text-lg font-medium">No data available</div>
        </div>
      );
    }
    
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="text-lg font-medium">Loading chart data...</div>
        </div>
      );
    }
    
    if (error) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="text-lg font-medium text-red-500">Error: {error}</div>
        </div>
      );
    }
    
    // Log the chart data for debugging
    console.log('Rendering chart with data:', chartData);
    
    try {
      switch (chartType) {
        case 'bar':
          // For bar chart data from backend
          if (chartData.type === 'bar') {
            return (
              <BarChart 
                width={chartWidth} 
                height={chartHeight} 
                data={chartData.categories.map((cat: string, i: number) => ({
                  name: cat,
                  value: chartData.values[i],
                  color: chartData.colors[i]
                }))} 
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" name="Value">
                  {chartData.categories.map((cat: string, index: number) => (
                    <Cell key={`cell-${index}`} fill={chartData.colors[index]} />
                  ))}
                </Bar>
              </BarChart>
            );
          } else {
            console.error('Expected bar chart data but got:', chartData);
            return (
              <div className="flex items-center justify-center h-64">
                <div className="text-lg font-medium text-red-500">
                  Error: Unexpected data format for bar chart. Check console for details.
                </div>
              </div>
            );
          }
        
        case 'line':
          // For line chart data from backend
          if (chartData.type === 'line') {
            const lineData = chartData.dates.map((date: string, i: number) => {
              const dataPoint: any = { name: date };
              chartData.series.forEach((series: any) => {
                dataPoint[series.name] = series.values[i];
              });
              return dataPoint;
            });
            
            return (
              <LineChart 
                width={chartWidth} 
                height={chartHeight} 
                data={lineData} 
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                {chartData.series.map((series: any, i: number) => (
                  <Line 
                    key={`line-${i}`}
                    type="monotone" 
                    dataKey={series.name} 
                    stroke={series.color} 
                    activeDot={{ r: 8 }} 
                  />
                ))}
              </LineChart>
            );
          } else {
            console.error('Expected line chart data but got:', chartData);
            return (
              <div className="flex items-center justify-center h-64">
                <div className="text-lg font-medium text-red-500">
                  Error: Unexpected data format for line chart. Check console for details.
                </div>
              </div>
            );
          }
        
        case 'pie':
          // For pie chart data from backend
          if (chartData.type === 'pie') {
            return (
              <PieChart width={chartWidth} height={chartHeight}>
                <Pie
                  data={chartData.segments.map((seg: string, i: number) => ({
                    name: seg,
                    value: chartData.values[i],
                    color: chartData.colors[i]
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, percent }: { name: string, percent: number }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.segments.map((seg: string, index: number) => (
                    <Cell key={`cell-${index}`} fill={chartData.colors[index]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            );
          } else {
            console.error('Expected pie chart data but got:', chartData);
            return (
              <div className="flex items-center justify-center h-64">
                <div className="text-lg font-medium text-red-500">
                  Error: Unexpected data format for pie chart. Check console for details.
                </div>
              </div>
            );
          }
        
        default:
          return (
            <div className="flex items-center justify-center h-64">
              <div className="text-lg font-medium text-red-500">
                Error: Unknown chart type: {chartType}
              </div>
            </div>
          );
      }
    } catch (error) {
      console.error('Error rendering chart:', error);
      return (
        <div className="flex items-center justify-center h-64">
          <div className="text-lg font-medium text-red-500">
            Error rendering chart. Check console for details.
          </div>
        </div>
      );
    }
  };
  
  // Function to regenerate data
  const [key, setKey] = useState<number>(0);
  const regenerateData = () => {
    setKey(prev => prev + 1);
    fetchChartData();
  };
  
  return (
    <div className="p-8 bg-white rounded-lg shadow flex flex-col items-center justify-center">
      <h2 className="text-2xl font-bold mb-4">Chart Visualizer</h2>
      
      <div className="mb-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Chart Type</label>
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value as any)}
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="bar">Bar Chart</option>
            <option value="line">Line Chart</option>
            <option value="pie">Pie Chart</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {chartType === 'bar' ? 'Number of Categories' : 
             chartType === 'line' ? 'Number of Points' : 
             'Number of Segments'}
          </label>
          <input
            type="number"
            min="2"
            max="20"
            value={numItems}
            onChange={(e) => setNumItems(parseInt(e.target.value))}
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        
        {chartType === 'line' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Number of Series</label>
            <input
              type="number"
              min="1"
              max="5"
              value={numSeries}
              onChange={(e) => setNumSeries(parseInt(e.target.value))}
              className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        )}
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Min Value</label>
          <input
            type="number"
            value={minValue}
            onChange={(e) => setMinValue(parseInt(e.target.value))}
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Max Value</label>
          <input
            type="number"
            value={maxValue}
            onChange={(e) => setMaxValue(parseInt(e.target.value))}
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        
        <div className="md:col-span-2 lg:col-span-4">
          <button
            onClick={regenerateData}
            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Refresh Chart
          </button>
        </div>
      </div>
      
      <div key={key} className="w-full h-64 mt-4 flex justify-center">
        {renderChart()}
      </div>
      
      <div className="mt-4 p-4 bg-gray-100 rounded-lg">
        <p className="text-sm text-gray-600">
          This Chart Visualizer component fetches data from the chart_data_generator agent.
          You can customize the chart parameters and refresh to get new data.
        </p>
      </div>
    </div>
  );
};
