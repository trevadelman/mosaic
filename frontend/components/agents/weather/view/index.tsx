"use client";

import { AgentView, AgentViewProps } from "@/lib/types/agent-view";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

// Types for structured data
interface Location {
  name: string;
  country: string;
  admin1: string;
  latitude: number;
  longitude: number;
  population: number | null;
  display_name: string;
}

interface LocationSearchResult {
  locations: Location[];
  error?: string;
}

interface CurrentWeather {
  location: {
    name: string;
    coordinates: {
      latitude: number;
      longitude: number;
    };
    timezone: string;
  };
  current: {
    temperature: {
      celsius: number;
      fahrenheit: number;
    };
    feels_like: {
      celsius: number;
      fahrenheit: number;
    };
    humidity: number;
    weather: {
      code: number;
      description: string;
      emoji: string;
    };
    precipitation: {
      total: number;
      rain: number;
      showers: number;
      snowfall: number;
    };
    cloud_cover: number;
    pressure: {
      msl: number;
      surface: number;
    };
    wind: {
      speed: {
        kmh: number;
        mph: number;
      };
      direction: number;
      gusts: {
        kmh: number;
        mph: number;
      };
    };
    is_day: boolean;
    timestamp: string;
  };
  meta: {
    source: string;
    retrieved_at: string;
  };
  error?: string;
}

interface ForecastDay {
  date: string;
  weather: {
    code: number;
    description: string;
    emoji: string;
  };
  temperature: {
    min: {
      celsius: number;
      fahrenheit: number;
    };
    max: {
      celsius: number;
      fahrenheit: number;
    };
  };
  feels_like: {
    min: {
      celsius: number;
      fahrenheit: number;
    };
    max: {
      celsius: number;
      fahrenheit: number;
    };
  };
  sun: {
    sunrise: string;
    sunset: string;
  };
  precipitation: {
    sum: number;
    rain_sum: number;
    showers_sum: number;
    snowfall_sum: number;
    hours: number;
    probability: number;
  };
  wind: {
    speed_max: {
      kmh: number;
      mph: number;
    };
    gusts_max: {
      kmh: number;
      mph: number;
    };
    direction: number;
  };
}

interface WeatherForecast {
  location: {
    name: string;
    coordinates: {
      latitude: number;
      longitude: number;
    };
    timezone: string;
  };
  forecast: {
    days: ForecastDay[];
  };
  meta: {
    source: string;
    retrieved_at: string;
  };
  error?: string;
}

interface TemperatureData {
  city: string;
  temperature_celsius: number;
  error?: string;
}

// Helper function to parse JSON responses
const parseJsonResponse = (response: any) => {
  if (typeof response === 'string') {
    try {
      return JSON.parse(response);
    } catch (e) {
      console.error('Error parsing JSON response:', e);
      return { error: 'Invalid response format' };
    }
  }
  return response;
};

// Helper function to format date
const formatDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

// Helper function to format time
const formatTime = (timeString: string) => {
  const options: Intl.DateTimeFormatOptions = { 
    hour: 'numeric', 
    minute: 'numeric',
    hour12: true
  };
  return new Date(timeString).toLocaleTimeString(undefined, options);
};

// Helper function to get wind direction as text
const getWindDirection = (degrees: number) => {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const index = Math.round(degrees / 22.5) % 16;
  return directions[index];
};

// Current Weather Component
const CurrentWeatherDisplay: React.FC<{
  currentWeather: CurrentWeather | null;
  loading: boolean;
  error: string | null;
  useFahrenheit: boolean;
}> = ({ currentWeather, loading, error, useFahrenheit }) => {
  if (loading) {
    return <div className="flex justify-center p-8">Loading current weather...</div>;
  }

  if (error) {
    return (
      <div className="p-3 rounded bg-red-100 text-red-800">
        {error}
      </div>
    );
  }

  if (!currentWeather) {
    return (
      <div className="p-6 text-center text-gray-500">
        Search for a location to view current weather
      </div>
    );
  }

  if (currentWeather.error) {
    return (
      <div className="p-3 rounded bg-red-100 text-red-800">
        {currentWeather.error}
      </div>
    );
  }

  const { location, current } = currentWeather;
  const temp = useFahrenheit ? current.temperature.fahrenheit : current.temperature.celsius;
  const feelsLike = useFahrenheit ? current.feels_like.fahrenheit : current.feels_like.celsius;
  const windSpeed = useFahrenheit ? current.wind.speed.mph : current.wind.speed.kmh;
  const windGust = useFahrenheit ? current.wind.gusts.mph : current.wind.gusts.kmh;
  const windUnit = useFahrenheit ? "mph" : "km/h";
  const tempUnit = useFahrenheit ? "°F" : "°C";

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold">{location.name}</h2>
          <p className="text-gray-500">
            {new Date(current.timestamp).toLocaleString()}
          </p>
        </div>
        <div className="flex items-center mt-2 md:mt-0">
          <span className="text-5xl mr-4">{current.weather.emoji}</span>
          <div>
            <div className="text-4xl font-bold">{temp.toFixed(1)}{tempUnit}</div>
            <div className="text-gray-500">Feels like {feelsLike.toFixed(1)}{tempUnit}</div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Weather</h3>
          <p className="text-lg">{current.weather.description}</p>
        </Card>
        
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Humidity</h3>
          <p className="text-lg">{current.humidity}%</p>
        </Card>
        
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Cloud Cover</h3>
          <p className="text-lg">{current.cloud_cover}%</p>
        </Card>
        
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Wind</h3>
          <p className="text-lg">
            {windSpeed.toFixed(1)} {windUnit} {getWindDirection(current.wind.direction)}
          </p>
          <p className="text-sm text-gray-500">
            Gusts: {windGust.toFixed(1)} {windUnit}
          </p>
        </Card>
        
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Precipitation</h3>
          <p className="text-lg">{current.precipitation.total} mm</p>
          {current.precipitation.rain > 0 && (
            <p className="text-sm text-gray-500">Rain: {current.precipitation.rain} mm</p>
          )}
          {current.precipitation.snowfall > 0 && (
            <p className="text-sm text-gray-500">Snow: {current.precipitation.snowfall} cm</p>
          )}
        </Card>
        
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Pressure</h3>
          <p className="text-lg">{current.pressure.msl} hPa</p>
        </Card>
      </div>
      
      <div className="text-xs text-gray-400 text-right">
        Data source: {currentWeather.meta.source}
      </div>
    </div>
  );
};

// Forecast Component
const ForecastDisplay: React.FC<{
  forecast: WeatherForecast | null;
  loading: boolean;
  error: string | null;
  useFahrenheit: boolean;
}> = ({ forecast, loading, error, useFahrenheit }) => {
  if (loading) {
    return <div className="flex justify-center p-8">Loading forecast...</div>;
  }

  if (error) {
    return (
      <div className="p-3 rounded bg-red-100 text-red-800">
        {error}
      </div>
    );
  }

  if (!forecast) {
    return (
      <div className="p-6 text-center text-gray-500">
        Search for a location to view forecast
      </div>
    );
  }

  if (forecast.error) {
    return (
      <div className="p-3 rounded bg-red-100 text-red-800">
        {forecast.error}
      </div>
    );
  }

  const { location, forecast: forecastData } = forecast;
  const tempUnit = useFahrenheit ? "°F" : "°C";
  const speedUnit = useFahrenheit ? "mph" : "km/h";

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">{location.name} - 5-Day Forecast</h2>
      
      <div className="space-y-4">
        {forecastData.days.map((day, index) => {
          const minTemp = useFahrenheit ? day.temperature.min.fahrenheit : day.temperature.min.celsius;
          const maxTemp = useFahrenheit ? day.temperature.max.fahrenheit : day.temperature.max.celsius;
          const windSpeed = useFahrenheit ? day.wind.speed_max.mph : day.wind.speed_max.kmh;
          
          return (
            <Card key={index} className="p-4">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                <div className="mb-2 md:mb-0">
                  <h3 className="font-bold">{formatDate(day.date)}</h3>
                  <p className="text-gray-500">{day.weather.description}</p>
                </div>
                
                <div className="flex items-center">
                  <span className="text-3xl mr-3">{day.weather.emoji}</span>
                  <div>
                    <div className="font-medium">
                      {minTemp.toFixed(1)}{tempUnit} - {maxTemp.toFixed(1)}{tempUnit}
                    </div>
                  </div>
                </div>
              </div>
              
              <Separator className="my-3" />
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Precipitation</h4>
                  <p>{day.precipitation.sum} mm</p>
                  <p className="text-sm text-gray-500">Probability: {day.precipitation.probability}%</p>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Wind</h4>
                  <p>{windSpeed.toFixed(1)} {speedUnit} {getWindDirection(day.wind.direction)}</p>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Sun</h4>
                  <p>Rise: {formatTime(day.sun.sunrise)}</p>
                  <p>Set: {formatTime(day.sun.sunset)}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
      
      <div className="text-xs text-gray-400 text-right">
        Data source: {forecast.meta.source}
      </div>
    </div>
  );
};

// Simple Temperature Component
const TemperatureDisplay: React.FC<{
  temperatureData: TemperatureData | null;
  loading: boolean;
  error: string | null;
  useFahrenheit: boolean;
}> = ({ temperatureData, loading, error, useFahrenheit }) => {
  if (loading) {
    return <div className="flex justify-center p-8">Loading temperature...</div>;
  }

  if (error) {
    return (
      <div className="p-3 rounded bg-red-100 text-red-800">
        {error}
      </div>
    );
  }

  if (!temperatureData) {
    return (
      <div className="p-6 text-center text-gray-500">
        Search for a location to view temperature
      </div>
    );
  }

  if (temperatureData.error) {
    return (
      <div className="p-3 rounded bg-red-100 text-red-800">
        {temperatureData.error}
      </div>
    );
  }

  const tempCelsius = temperatureData.temperature_celsius;
  const tempFahrenheit = (tempCelsius * 9/5) + 32;
  const temp = useFahrenheit ? tempFahrenheit : tempCelsius;
  const tempUnit = useFahrenheit ? "°F" : "°C";

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <h2 className="text-2xl font-bold mb-4">{temperatureData.city}</h2>
      <div className="text-6xl font-bold mb-2">{temp.toFixed(1)}{tempUnit}</div>
      <div className="text-gray-500">
        {useFahrenheit ? `${tempCelsius.toFixed(1)}°C` : `${tempFahrenheit.toFixed(1)}°F`}
      </div>
    </div>
  );
};

// Main Weather View Component
const WeatherViewComponent: React.FC<AgentViewProps> = ({ tools }) => {
  // State for location search
  const [searchQuery, setSearchQuery] = useState("");
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  
  // State for weather data
  const [currentWeather, setCurrentWeather] = useState<CurrentWeather | null>(null);
  const [forecast, setForecast] = useState<WeatherForecast | null>(null);
  const [temperatureData, setTemperatureData] = useState<TemperatureData | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState<string | null>(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState("current");
  const [useFahrenheit, setUseFahrenheit] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  
  // Handle location search
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setSearchLoading(true);
    setSearchError(null);
    setLocations([]);
    setShowSearchResults(true);
    
    try {
      const result = await tools.search_location(searchQuery);
      const parsedResult = parseJsonResponse(result) as LocationSearchResult;
      
      if (parsedResult.error) {
        setSearchError(parsedResult.error);
      } else if (parsedResult.locations && parsedResult.locations.length > 0) {
        setLocations(parsedResult.locations);
      } else {
        setSearchError("No locations found");
      }
    } catch (err) {
      console.error("Error searching for location:", err);
      setSearchError("Failed to search for location. Please try again.");
    } finally {
      setSearchLoading(false);
    }
  };
  
  // Handle location selection
  const handleSelectLocation = async (location: Location) => {
    setSelectedLocation(location);
    setShowSearchResults(false);
    setWeatherLoading(true);
    setWeatherError(null);
    
    try {
      // Get current weather
      if (activeTab === "current") {
        const result = await tools.get_current_weather(location.latitude, location.longitude);
        const parsedResult = parseJsonResponse(result) as CurrentWeather;
        setCurrentWeather(parsedResult);
      } 
      // Get forecast
      else if (activeTab === "forecast") {
        const result = await tools.get_weather_forecast(location.latitude, location.longitude, 5);
        const parsedResult = parseJsonResponse(result) as WeatherForecast;
        setForecast(parsedResult);
      }
      // Get simple temperature
      else if (activeTab === "temperature") {
        const result = await tools.get_temperature(location.display_name);
        const parsedResult = parseJsonResponse(result) as TemperatureData;
        setTemperatureData(parsedResult);
      }
    } catch (err) {
      console.error("Error getting weather data:", err);
      setWeatherError("Failed to get weather data. Please try again.");
    } finally {
      setWeatherLoading(false);
    }
  };
  
  // Handle tab change
  const handleTabChange = async (tab: string) => {
    setActiveTab(tab);
    
    // If a location is already selected, fetch data for the new tab
    if (selectedLocation) {
      setWeatherLoading(true);
      setWeatherError(null);
      
      try {
        // Get current weather
        if (tab === "current") {
          const result = await tools.get_current_weather(selectedLocation.latitude, selectedLocation.longitude);
          const parsedResult = parseJsonResponse(result) as CurrentWeather;
          setCurrentWeather(parsedResult);
        } 
        // Get forecast
        else if (tab === "forecast") {
          const result = await tools.get_weather_forecast(selectedLocation.latitude, selectedLocation.longitude, 5);
          const parsedResult = parseJsonResponse(result) as WeatherForecast;
          setForecast(parsedResult);
        }
        // Get simple temperature
        else if (tab === "temperature") {
          const result = await tools.get_temperature(selectedLocation.display_name);
          const parsedResult = parseJsonResponse(result) as TemperatureData;
          setTemperatureData(parsedResult);
        }
      } catch (err) {
        console.error("Error getting weather data:", err);
        setWeatherError("Failed to get weather data. Please try again.");
      } finally {
        setWeatherLoading(false);
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-6">Weather Information</h1>
        
        {/* Search bar */}
        <div className="flex gap-2 mb-2">
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Enter city or location..."
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="flex-1"
          />
          <Button 
            onClick={handleSearch}
            disabled={searchLoading}
          >
            {searchLoading ? "Searching..." : "Search"}
          </Button>
          
          <div className="flex items-center ml-2">
            <Switch
              id="unit-toggle"
              checked={useFahrenheit}
              onCheckedChange={setUseFahrenheit}
              className="mr-2"
            />
            <Label htmlFor="unit-toggle" className="text-sm">
              {useFahrenheit ? "°F" : "°C"}
            </Label>
          </div>
        </div>
        
        {/* Search error */}
        {searchError && (
          <div className="p-3 rounded bg-red-100 text-red-800 mb-4">
            {searchError}
          </div>
        )}
        
        {/* Search results */}
        {showSearchResults && locations.length > 0 && (
          <Card className="p-4 mb-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Select a location:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-60 overflow-y-auto">
              {locations.map((location, index) => (
                <Card 
                  key={index} 
                  className="p-3 hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => handleSelectLocation(location)}
                >
                  <div className="font-medium">{location.name}</div>
                  <div className="text-sm text-gray-500">
                    {location.admin1 && `${location.admin1}, `}{location.country}
                  </div>
                  {location.population && (
                    <div className="text-xs text-gray-400">
                      Population: {location.population.toLocaleString()}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </Card>
        )}
      </div>
      
      {/* Weather display */}
      <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="current">
            <span className="mr-2">🌡️</span> Current Weather
          </TabsTrigger>
          <TabsTrigger value="forecast">
            <span className="mr-2">📅</span> Forecast
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="current">
          <CurrentWeatherDisplay
            currentWeather={currentWeather}
            loading={weatherLoading}
            error={weatherError}
            useFahrenheit={useFahrenheit}
          />
        </TabsContent>
        
        <TabsContent value="forecast">
          <ForecastDisplay
            forecast={forecast}
            loading={weatherLoading}
            error={weatherError}
            useFahrenheit={useFahrenheit}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Export the view configuration
const WeatherView: AgentView = {
  layout: 'full',
  components: {
    main: WeatherViewComponent
  },
  tools: [
    'search_location',
    'get_current_weather',
    'get_weather_forecast',
    'get_temperature'
  ]
};

export default WeatherView;
