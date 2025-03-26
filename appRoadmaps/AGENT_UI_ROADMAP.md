# MOSAIC Agent UI Implementation Roadmap

## Table of Contents
1. [Overview](#overview)
2. [Phase 1: Foundation](#phase-1-foundation)
3. [Phase 2: Core Systems](#phase-2-core-systems)
4. [Phase 3: Integration](#phase-3-integration)
4. [Phase 4: Tool Invocation](#phase-4-tool-invocation)
5. [Phase 5: Structured Output](#phase-5-structured-output)
6. [Phase 6: Example Agent](#phase-6-example-agent)
7. [Phase 7: Testing & Refinement](#phase-7-testing--refinement)
8. [Future Enhancements](#future-enhancements)

## Overview

This roadmap outlines the implementation steps for the MOSAIC Agent UI Framework as specified in `AGENT_UI_FRAMEWORK.md`. We'll follow an iterative approach, starting with a specific agent view and building out the framework to support it.

### Implementation Philosophy
- Build based on real needs
- Test with actual data
- Iterate on feedback
- Maintain flexibility
- Document as we go

## Phase 1: Foundation

### 1.1 Project Structure
```
frontend/
  components/
    agents/
      [agent-name]/
        view/
          index.tsx
          components/
          hooks/
          types.ts
```

### 1.2 Base Types
Reference: [Type System in Framework Spec](AGENT_UI_FRAMEWORK.md#type-system)

```typescript
// lib/types/agent-view.ts
export interface AgentView {
  layout: 'full' | 'split' | 'dashboard';
  components: Record<string, React.ComponentType>;
  tools: string[];
}

export interface ViewComponent<T = any> {
  (props: T & AgentViewProps): JSX.Element;
}
```

### 1.3 Route Setup
```typescript
// app/agents/[name]/view/page.tsx
export default function AgentViewPage({ params }: { params: { name: string } }) {
  const { agent } = useAgent(params.name);
  
  if (!agent.hasCustomView) {
    return <NotFoundPage />;
  }
  
  return <AgentViewContainer agent={agent} />;
}
```

### 1.4 Layout Components
- ViewContainer with layout variants
- Responsive design system
- Theme integration
- Layout configuration options

## Phase 2: Core Systems

### 2.1 Tool Access Layer
Reference: [Tool Access Layer in Framework Spec](AGENT_UI_FRAMEWORK.md#tool-access-layer)

```typescript
// lib/hooks/use-agent-tools.ts
export const useAgentTools = (agentId: string) => {
  const invoke = async (name: string, ...args: any[]) => {
    const response = await fetch(`/api/agents/${agentId}/tools/${name}`, {
      method: 'POST',
      body: JSON.stringify({ args })
    });
    return response.json();
  };
  
  const stream = async function* (name: string, ...args: any[]) {
    const response = await fetch(`/api/agents/${agentId}/tools/${name}/stream`, {
      method: 'POST',
      body: JSON.stringify({ args })
    });
    
    const reader = response.body!.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      yield JSON.parse(new TextDecoder().decode(value));
    }
  };
  
  return { invoke, stream };
};
```

### 2.2 Update System
Reference: [Real-time Updates in Framework Spec](AGENT_UI_FRAMEWORK.md#real-time-updates)

```typescript
// lib/updates/index.ts
export class UpdateSystem {
  private ws: WebSocket;
  private handlers = new Map<string, Set<UpdateHandler>>();
  
  constructor(agentId: string) {
    this.ws = new WebSocket(`ws://localhost:8000/agents/${agentId}/updates`);
    this.setupHandlers();
  }
  
  subscribe(channel: string, handler: UpdateHandler) {
    if (!this.handlers.has(channel)) {
      this.handlers.set(channel, new Set());
    }
    this.handlers.get(channel)!.add(handler);
    return () => this.unsubscribe(channel, handler);
  }
  
  private setupHandlers() {
    this.ws.onmessage = (event) => {
      const { channel, data } = JSON.parse(event.data);
      this.handlers.get(channel)?.forEach(handler => handler(data));
    };
  }
}
```

### 2.3 State Management
Reference: [State Management in Framework Spec](AGENT_UI_FRAMEWORK.md#state-management)

```typescript
// lib/hooks/use-view-state.ts
export const useViewState = <T extends object>(initialState: T) => {
  const [state, setState] = useState<T>(initialState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | undefined>();
  
  const update = useCallback((newData: Partial<T>) => {
    setState(prev => ({ ...prev, ...newData }));
  }, []);
  
  return {
    data: state,
    loading,
    error,
    update,
    setLoading,
    setError
  };
};
```

## Phase 3: Integration

### 3.1 Agent Extension
```python
# backend/agents/base.py
class BaseAgent:
    has_custom_view: bool = False
    custom_view: Optional[Dict[str, Any]] = None
    
    def get_view_config(self) -> Dict[str, Any]:
        """Get the view configuration for this agent."""
        if not self.has_custom_view:
            return {}
        
        return {
            "name": self.custom_view.get("name", self.name),
            "layout": self.custom_view.get("layout", "full"),
            "capabilities": self.custom_view.get("capabilities", [])
        }
```

### 3.2 UI Badge Implementation
```typescript
// frontend/components/agents/agent-selector.tsx
import { Layout } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

// Inside the AgentSelector component
{agent.hasCustomView && (
  <Link href={`/agents/${agent.id}/view`} onClick={(e) => e.stopPropagation()}>
    <Badge 
      variant="outline" 
      className="ml-2 bg-blue-100 text-blue-800 hover:bg-blue-200 cursor-pointer"
    >
      <Layout className="h-3 w-3 mr-1" />
      UI
    </Badge>
  </Link>
)}
```

#### Backend API Integration
```typescript
// In agent_api.py
def _extract_agent_metadata(self, agent_id: str, agent: Any) -> Dict[str, Any]:
    # ... existing code ...
    
    # Add custom view properties if available
    if hasattr(agent, "has_custom_view"):
        metadata["hasCustomView"] = agent.has_custom_view
        if hasattr(agent, "custom_view") and agent.custom_view:
            metadata["customView"] = agent.custom_view
    
    return metadata
```

#### Requirements for UI Badge
1. The agent must have `has_custom_view` set to `True`
2. The agent's metadata must be properly exposed through the API
3. The frontend must include the badge component in the agent card
4. The agent must have a corresponding view component registered
5. The URL must use the agent's ID (not name) to avoid capitalization issues

### 3.3 View Discovery
```typescript
// lib/view-discovery.ts
export class ViewDiscovery {
  private views = new Map<string, () => Promise<AgentView>>();
  
  async discoverViews() {
    const viewModules = import.meta.glob(
      '../components/agents/*/view/index.tsx'
    );
    
    for (const [path, importFn] of Object.entries(viewModules)) {
      const agentName = this.extractAgentName(path);
      this.views.set(agentName, importFn);
    }
  }
  
  async loadView(agentName: string): Promise<AgentView | undefined> {
    const importFn = this.views.get(agentName);
    if (!importFn) return undefined;
    
    const module = await importFn();
    return module.default;
  }
}
```

### 3.3 WebSocket Enhancement
```typescript
// lib/websocket.ts
class AgentViewSocket extends WebSocketService {
  subscribeToView(agentId: string, handler: UpdateHandler) {
    this.send({
      type: 'subscribe_view',
      agentId
    });
    
    this.addHandler(agentId, handler);
  }
  
  sendViewAction(agentId: string, action: string, data: any) {
    this.send({
      type: 'view_action',
      agentId,
      action,
      data
    });
  }
}
```

## Phase 4: Tool Invocation

### 4.1 Chat-Based Tool Invocation
Reference: [Tool Invocation Best Practices in Framework Spec](AGENT_UI_FRAMEWORK.md#tool-invocation-best-practices)

```typescript
// lib/hooks/use-chat-tools.ts
export const useChatTools = (agentId: string) => {
  const invokeToolThroughChat = async (toolName: string, ...args: any[]) => {
    // Format the message to instruct the agent to use a specific tool
    let message = `Use the ${toolName} tool with the following parameters:\n\n`;
    
    // Format the parameters based on the tool
    if (toolName === 'search_location') {
      // For search_location, the first argument is the query
      const query = args[0];
      message += `query: "${query}"`;
    } else if (toolName === 'get_weather_forecast_by_coordinates') {
      // For get_weather_forecast_by_coordinates, we need latitude, longitude, and days
      let latitude, longitude, days;
      
      if (typeof args[0] === 'object' && args[0] !== null) {
        // If first argument is an object with parameters
        const params = args[0];
        latitude = params.latitude || params.lat;
        longitude = params.longitude || params.lon;
        days = params.days || 5;
      } else {
        // If parameters are passed individually
        latitude = args[0];
        longitude = args[1];
        days = args[2] || 5;
      }
      
      message += `latitude: ${latitude}\nlongitude: ${longitude}\ndays: ${days}`;
    } else {
      // For other tools, just stringify the arguments
      message += `Arguments: ${JSON.stringify(args)}`;
    }
    
    // Send the message to the agent
    const response = await chatApi.sendMessage(agentId, message);
    
    // Get the agent's response
    const messages = await chatApi.getMessages(agentId);
    
    // Find the latest assistant message
    const assistantMessages = messages.data.filter(m => m.role === 'assistant');
    const latestMessage = assistantMessages[assistantMessages.length - 1];
    
    // Return the content of the latest assistant message
    return latestMessage.content;
  };
  
  // Create a proxy object that allows tools to be called directly
  const tools = new Proxy({}, {
    get: (target, prop) => {
      if (typeof prop === 'string') {
        return (...args: any[]) => invokeToolThroughChat(prop, ...args);
      }
      return undefined;
    }
  });
  
  return tools;
};
```

### 4.2 Component Communication in Split Views

```typescript
// lib/hooks/use-component-communication.ts
export const useComponentCommunication = (updates: UpdateSystem) => {
  // Event-based communication
  const publishEvent = (channel: string, data: any) => {
    updates.publish(channel, data);
  };
  
  const subscribeToEvent = (channel: string, handler: (data: any) => void) => {
    return updates.subscribe(channel, handler);
  };
  
  // Function-based communication
  const registerFunction = (channel: string, fn: (data: any) => void) => {
    updates.publish(`register-${channel}`, fn);
  };
  
  const getFunctionRef = (channel: string) => {
    const fnRef = useRef<((data: any) => void) | null>(null);
    
    useEffect(() => {
      const unsubscribe = updates.subscribe(`register-${channel}`, (fn) => {
        fnRef.current = fn;
      });
      
      return unsubscribe;
    }, [updates, channel]);
    
    return fnRef;
  };
  
  return {
    publishEvent,
    subscribeToEvent,
    registerFunction,
    getFunctionRef
  };
};
```

### 4.3 Error Handling and Debugging

```typescript
// lib/hooks/use-tool-error-handling.ts
export const useToolErrorHandling = (tools: any) => {
  const invokeWithErrorHandling = async (toolName: string, ...args: any[]) => {
    try {
      // Invoke the tool
      const result = await tools[toolName](...args);
      return {
        success: true,
        data: result,
        error: null
      };
    } catch (err) {
      console.error(`Error executing tool ${toolName}:`, err);
      
      // Handle different types of errors
      let errorMessage = 'An unknown error occurred';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      return {
        success: false,
        data: null,
        error: errorMessage
      };
    }
  };
  
  // Create a proxy object that wraps all tool calls with error handling
  const safeTools = new Proxy({}, {
    get: (target, prop) => {
      if (typeof prop === 'string' && typeof tools[prop] === 'function') {
        return (...args: any[]) => invokeWithErrorHandling(prop, ...args);
      }
      return undefined;
    }
  });
  
  return safeTools;
};
```

### 4.4 In-Memory Event System for Component Communication

```typescript
// lib/event-emitter.ts
export class EventEmitter {
  private events: Record<string, Array<(data: any) => void>> = {};

  subscribe(channel: string, handler: (data: any) => void): () => void {
    if (!this.events[channel]) {
      this.events[channel] = [];
    }
    this.events[channel].push(handler);
    
    return () => {
      this.events[channel] = this.events[channel].filter(h => h !== handler);
    };
  }

  publish(channel: string, data: any): void {
    if (this.events[channel]) {
      this.events[channel].forEach(handler => {
        try {
          handler(data);
        } catch (err) {
          console.error(`Error in event handler for channel ${channel}:`, err);
        }
      });
    }
  }
}

// lib/hooks/use-event-emitter.ts
export const useEventEmitter = () => {
  const eventEmitterRef = useRef<EventEmitter>(new EventEmitter());
  
  const updates = useMemo(() => ({
    subscribe: (channel: string, handler: (data: any) => void) => {
      return eventEmitterRef.current.subscribe(channel, handler);
    },
    publish: (channel: string, data: any) => {
      eventEmitterRef.current.publish(channel, data);
    }
  }), []);
  
  return updates;
};
```

## Phase 5: Structured Output

### 5.1 Structured Output Types
Reference: [Structured Output Handling in Framework Spec](AGENT_UI_FRAMEWORK.md#structured-output-handling)

```typescript
// lib/types/structured-output.ts
export interface StructuredResponse<T = any> {
  content: string;
  raw_data?: T;
}

export interface StructuredToolResponse<T = any> {
  result: string | T;
  error?: string;
}
```

### 5.2 Agent-Level Structured Output Implementation

```python
# backend/agents/base.py
class BaseAgent:
    # ... existing code ...
    
    def ensure_structured_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure that the agent's output is properly structured.
        This method can be overridden by subclasses to implement
        agent-specific structured output handling.
        """
        return result
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override to implement structured output handling.
        """
        # Call the parent invoke method
        result = super().invoke(state)
        
        # Apply structured output handling
        return self.ensure_structured_output(result)
```

### 5.3 Tool-Level Structured Output

```python
# backend/agents/regular/weather.py
@tool
def get_temperature(city: str) -> str:
    """
    Get the current temperature for a city.
    
    Args:
        city: The name of the city
        
    Returns:
        A JSON string containing the city name and current temperature
    """
    # Implementation...
    
    # Format as JSON string
    return json.dumps({
        "city": city_name,
        "temperature_celsius": temperature
    })
```

### 5.4 Frontend Structured Output Handling

```typescript
// lib/hooks/use-structured-output.ts
export const useStructuredOutput = () => {
  const parseStructuredOutput = (response: any) => {
    // If the response is already an object, return it
    if (typeof response === 'object' && response !== null) {
      return response;
    }
    
    // If the response is a string, try to parse it as JSON
    if (typeof response === 'string') {
      try {
        return JSON.parse(response);
      } catch (err) {
        console.error('Error parsing structured output:', err);
        return { text: response };
      }
    }
    
    // If the response is neither an object nor a string, return it as is
    return response;
  };
  
  return { parseStructuredOutput };
};
```

### 5.5 Structured Output Display Components

```typescript
// components/structured-output/index.tsx
export const StructuredOutputDisplay: React.FC<{ data: any }> = ({ data }) => {
  // If the data is an error, display it
  if (data?.error) {
    return <ErrorDisplay error={data.error} />;
  }
  
  // If the data is a weather response, display it
  if (data?.city && data?.temperature_celsius !== undefined) {
    return <WeatherDisplay city={data.city} temperature={data.temperature_celsius} />;
  }
  
  // If the data is a generic object, display it as JSON
  return <JsonDisplay data={data} />;
};

// components/structured-output/weather-display.tsx
export const WeatherDisplay: React.FC<{ city: string, temperature: number }> = ({ city, temperature }) => {
  return (
    <div className="weather-display">
      <h2>{city}</h2>
      <div className="temperature">
        <span className="value">{temperature}</span>
        <span className="unit">°C</span>
      </div>
    </div>
  );
};
```

## Phase 6: Example Agent

### 6.1 Weather Agent Implementation
Reference: [Tool Invocation Best Practices in Framework Spec](AGENT_UI_FRAMEWORK.md#tool-invocation-best-practices)

1. **Agent Definition with Comprehensive Structured Data**
```python
class WeatherAgent(BaseAgent):
    name = "weather"
    has_custom_view = True
    custom_view = {
        "name": "WeatherView",
        "layout": "full",  # Using full layout for better user experience
        "capabilities": ["location-search", "current-weather", "weather-forecast"]
    }
    
    @tool
    def search_location(self, query: str) -> str:
        """Search for a location by name and return matching results."""
        try:
            import requests
            search_response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": query,
                    "count": 5,  # Get top 5 results
                    "language": "en",
                    "format": "json"
                },
                timeout=10
            )
            
            # Check if the search request was successful
            search_response.raise_for_status()
            
            # Parse the search response
            search_data = search_response.json()
            
            # Check if results were found
            if not search_data.get("results"):
                error_msg = f"No locations found matching '{query}'"
                return json.dumps({"error": error_msg})
            
            # Format the results
            locations = []
            for result in search_data["results"]:
                location = {
                    "name": result["name"],
                    "country": result.get("country", ""),
                    "admin1": result.get("admin1", ""),
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "population": result.get("population", None),
                    "display_name": ""
                }
                
                # Create a display name
                display_name = result["name"]
                if result.get("admin1"):
                    display_name += f", {result['admin1']}"
                if result.get("country"):
                    display_name += f", {result['country']}"
                location["display_name"] = display_name
                
                locations.append(location)
            
            # Create the result as a JSON string
            result = json.dumps({
                "locations": locations
            })
            
            return result
        
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    @tool
    def get_current_weather(self, latitude: float, longitude: float) -> str:
        """Get detailed current weather for specific coordinates."""
        try:
            import requests
            
            # Try to get the location name from reverse geocoding
            try:
                search_response = requests.get(
                    "https://geocoding-api.open-meteo.com/v1/reverse",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "language": "en",
                        "format": "json"
                    },
                    timeout=10
                )
                
                # Check if the search request was successful
                search_response.raise_for_status()
                
                # Parse the search response
                search_data = search_response.json()
                
                # Get the location name
                location_name = "Unknown Location"
                if search_data.get("results") and len(search_data["results"]) > 0:
                    result = search_data["results"][0]
                    location_name = result["name"]
                    if result.get("admin1"):
                        location_name += f", {result['admin1']}"
                    if result.get("country"):
                        location_name += f", {result['country']}"
            except Exception as e:
                # If reverse geocoding fails, use a generic location name with coordinates
                location_name = f"Location at {latitude:.4f}, {longitude:.4f}"
            
            # Get the current weather
            weather_response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "apparent_temperature",
                        "is_day",
                        "precipitation",
                        "rain",
                        "showers",
                        "snowfall",
                        "weather_code",
                        "cloud_cover",
                        "pressure_msl",
                        "surface_pressure",
                        "wind_speed_10m",
                        "wind_direction_10m",
                        "wind_gusts_10m"
                    ],
                    "temperature_unit": "celsius",
                    "wind_speed_unit": "kmh",
                    "precipitation_unit": "mm",
                    "timezone": "auto"
                },
                timeout=10
            )
            
            # Check if the weather request was successful
            weather_response.raise_for_status()
            
            # Parse the weather response
            weather_data = weather_response.json()
            
            # Extract the current weather
            current = weather_data["current"]
            
            # Get the weather code description and emoji
            weather_code = current["weather_code"]
            weather_description = WEATHER_CODES.get(weather_code, "Unknown")
            weather_emoji = WEATHER_EMOJIS.get(weather_code, "🌡️")
            
            # Create the result
            result = {
                "location": {
                    "name": location_name,
                    "coordinates": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "timezone": weather_data.get("timezone", "Unknown")
                },
                "current": {
                    "temperature": {
                        "celsius": current["temperature_2m"],
                        "fahrenheit": round((current["temperature_2m"] * 9/5) + 32, 1)
                    },
                    "feels_like": {
                        "celsius": current["apparent_temperature"],
                        "fahrenheit": round((current["apparent_temperature"] * 9/5) + 32, 1)
                    },
                    "humidity": current["relative_humidity_2m"],
                    "weather": {
                        "code": weather_code,
                        "description": weather_description,
                        "emoji": weather_emoji
                    },
                    "precipitation": {
                        "total": current["precipitation"],
                        "rain": current["rain"],
                        "showers": current["showers"],
                        "snowfall": current["snowfall"]
                    },
                    "cloud_cover": current["cloud_cover"],
                    "pressure": {
                        "msl": current["pressure_msl"],
                        "surface": current["surface_pressure"]
                    },
                    "wind": {
                        "speed": {
                            "kmh": current["wind_speed_10m"],
                            "mph": round(current["wind_speed_10m"] * 0.621371, 1)
                        },
                        "direction": current["wind_direction_10m"],
                        "gusts": {
                            "kmh": current["wind_gusts_10m"],
                            "mph": round(current["wind_gusts_10m"] * 0.621371, 1)
                        }
                    },
                    "is_day": bool(current["is_day"]),
                    "timestamp": current["time"]
                },
                "meta": {
                    "source": "Open-Meteo API",
                    "retrieved_at": datetime.now().isoformat()
                }
            }
            
            # Convert to JSON string
            json_result = json.dumps(result)
            
            return json_result
        
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    @tool
    def get_weather_forecast(self, latitude: float, longitude: float, days: int = 5) -> str:
        """Get a weather forecast for specific coordinates."""
        # Similar implementation to get_current_weather but for forecast data
        # ...
    
    @tool
    def get_temperature(self, city: str) -> str:
        """Get the current temperature for a city."""
        # Extract just the city name if the input contains commas
        search_query = city.split(',')[0].strip() if ',' in city else city
        
        try:
            # Implementation that returns a JSON string
            # ...
            return json.dumps({
                "city": city_name,
                "temperature_celsius": temperature
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _get_default_prompt(self) -> str:
        """Get the default system prompt for the weather agent."""
        return (
            "You are a weather assistant that provides detailed weather information. "
            "Your job is to help users get weather information for any location they ask about. "
            "\n\n"
            "You have the following tools available:"
            "\n"
            "- search_location: Search for a location by name and return matching results."
            "\n"
            "- get_current_weather: Get detailed current weather for specific coordinates."
            "\n"
            "- get_weather_forecast: Get a weather forecast for specific coordinates."
            "\n"
            "- get_temperature: Get the current temperature for a city."
            "\n\n"
            "IMPORTANT: When you receive a JSON response from any tool, "
            "return it directly to the user without any additional text. "
            "Do not add any explanations, formatting, or other text. Just return the JSON object exactly as it is."
            "\n\n"
            "Example:"
            "\n"
            "User: What's the temperature in New York?"
            "\n"
            "You: {\"city\": \"New York, New York, United States\", \"temperature_celsius\": 22.5}"
        )
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override the invoke method to create a stateless agent that doesn't load previous conversations.
        Also intercept tool results to ensure structured output.
        """
        # Extract just the last message from the state
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            # Create a new state with just the last message
            new_state = {"messages": [last_message]}
        else:
            new_state = {"messages": []}
        
        # Call the parent invoke method with the new state
        result = super().invoke(new_state)
        
        # Extract the tool result from the messages
        for message in result.get("messages", []):
            if hasattr(message, "type") and message.type == "tool" and hasattr(message, "name") and hasattr(message, "result"):
                tool_name = message.name
                tool_result = message.result
                
                # Replace the last AI message with the tool result
                for i in range(len(result["messages"]) - 1, -1, -1):
                    if hasattr(result["messages"][i], "type") and result["messages"][i].type == "ai":
                        result["messages"][i].content = tool_result
                        break
                
                break
        
        return result
```

2. **View Components with Full Layout and Tabbed Interface**
```typescript
// components/agents/weather/view/index.tsx
export const WeatherView: AgentView = {
  layout: 'full',  // Using full layout instead of split
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
      
      {/* Weather display with tabs */}
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
```

### 6.2 Key Lessons from Weather Agent Implementation

1. **Comprehensive Structured Data**
   - Define clear TypeScript interfaces for all data structures
   - Include both raw data and formatted data (e.g., both Celsius and Fahrenheit)
   - Add metadata like source and timestamp
   - Include error information in the response structure

2. **Robust Error Handling**
   - Handle API failures gracefully
   - Provide fallbacks for missing data
   - Return structured error responses
   - Display user-friendly error messages

3. **Full Layout with Integrated UI**
   - Use a full layout for a cleaner user experience
   - Integrate search functionality directly in the main view
   - Use a tabbed interface for different data views
   - Provide unit toggles and other user preferences

4. **Stateless Agent Design**
   - Make the agent stateless to avoid loading previous conversations
   - Extract just the last message from the state
   - Intercept tool results to ensure structured output
   - Replace AI messages with tool results

### 6.2 Integration Testing
- Test tool invocation with real queries
- Verify structured output handling
- Test layout responsiveness
- Validate error handling

## Phase 7: Testing & Refinement

### 7.1 Performance Testing
- Component load times
- WebSocket message handling
- State updates
- Tool invocation latency

### 7.2 Error Handling
- Network failures
- Tool execution errors
- WebSocket disconnections
- State management errors

### 7.3 Documentation
- Update framework specification
- Add implementation guides
- Document best practices
- Create example templates

## Future Enhancements

### Phase 8: Advanced Features
1. **Multiple Views per Agent**
   - View switching system
   - State preservation between views
   - View-specific tools

2. **State Persistence**
   - Local storage integration
   - Session management
   - State migration

3. **Enhanced Real-time Features**
   - Bi-directional streaming
   - Custom update frequencies
   - Throttling/debouncing system

4. **Advanced Layouts**
   - Custom layout definitions
   - Dynamic grid systems
   - Responsive breakpoints

### Phase 9: Developer Experience
1. **CLI Tools**
   - View scaffolding
   - Component generation
   - Testing utilities

2. **Development Tools**
   - View debugger
   - State inspector
   - Performance monitoring

3. **Documentation**
   - Interactive examples
   - Video tutorials
   - Best practices guide

## Implementation Notes

1. **Framework Alignment**
   - Regularly review `AGENT_UI_FRAMEWORK.md` for alignment
   - Update framework spec as needed
   - Document deviations and rationale

2. **Testing Strategy**
   - Test with real data and tools
   - No mock data in production
   - Performance testing in production environment

3. **Flexibility**
   - Keep framework extensible
   - Allow for future enhancements
   - Maintain backward compatibility

4. **Documentation**
   - Update docs with implementation details
   - Include real-world examples
   - Document edge cases and solutions

5. **Tool Invocation Best Practices**
   - Use chat-based tool invocation for consistency
   - Implement proper error handling
   - Add debugging capabilities
   - Support multiple parameter formats

6. **Structured Output Best Practices**
   - Prefer tool-level formatting for simple data
   - Use agent prompt engineering for consistent output
   - Implement response interception for complex cases
   - Handle different response formats in the frontend

This roadmap provides a structured approach to implementing the Agent UI Framework while maintaining flexibility for future enhancements and changes based on real-world usage.
