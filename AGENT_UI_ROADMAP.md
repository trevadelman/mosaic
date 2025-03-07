# Hybrid Agent-UI Framework Roadmap

This roadmap outlines the implementation plan for integrating UI components with the existing agent framework using a hybrid approach based on composition.

## Phase 1: Foundation & Architecture

### Core Registry Structure

- [x] Create `UIComponentRegistry` class with similar patterns to `AgentRegistry`
  - [x] Implement singleton pattern
  - [x] Add component storage
  - [x] Add registration methods
  - [x] Add retrieval methods
  - [x] Add logging

- [x] Extend `AgentRegistry` class to reference UI components
  - [x] Add `ui_components` dictionary to store agent-component associations
  - [x] Add methods to register UI components with agents
  - [x] Add methods to retrieve UI components for agents
  - [x] Ensure backward compatibility

### Component Base Classes

- [x] Create `UIComponent` base class
  - [x] Define required properties (id, name, description)
  - [x] Define registration data structure
  - [x] Define handler registration methods
  - [x] Define event handling interface

- [x] Create component type interfaces
  - [x] Define visualization component interface
  - [x] Define interactive component interface
  - [x] Define data input component interface

### Completed Work

The following work has been completed for Phase 1:

```
feat: Implement UI component interfaces and mock implementations

- Created UIComponent base class and UIComponentRegistry
- Extended AgentRegistry to reference UI components
- Created component type interfaces:
  - VisualizationComponent
  - InteractiveComponent
  - DataInputComponent
- Created mock implementations with clear TODOs for replacement
- Updated roadmap with mock data strategy
```

### Discovery Mechanism

- [x] Extend agent discovery to include UI components
  - [x] Create directory structure for UI components
  - [x] Implement module discovery for UI components
  - [x] Define naming conventions for component files
  - [x] Add auto-registration during discovery

- [x] Implement component validation
  - [x] Validate required methods and properties
  - [x] Validate handler signatures
  - [x] Validate registration data

### Completed Work

The following work has been completed for the Discovery Mechanism:

```
feat: Implement UI component discovery and WebSocket handler

- Created UIComponentDiscovery class for discovering UI components
- Integrated UI component discovery with application startup
- Updated WebSocket handler to use the UI component registry
- Added fallback to hardcoded stock chart logic for backward compatibility
```

## Phase 2: WebSocket Handler Refactoring

### Modular Event Handling

- [x] Refactor `ui_websocket_handler.py` to use the registry
  - [x] Remove hardcoded stock chart logic
  - [x] Implement dynamic handler dispatch
  - [x] Add comprehensive error handling
  - [x] Implement event logging

- [x] Create handler registration system
  - [x] Define standard handler signature
  - [x] Implement handler lookup by component and action
  - [x] Add default handlers for common actions

### Completed Work

The following work has been completed for WebSocket Handler Refactoring:

```
feat: Refactor WebSocket handler to use component registry

- Removed hardcoded stock chart logic from ui_websocket_handler.py
- Implemented dynamic handler dispatch based on component registry
- Added comprehensive error handling for component and handler lookup
- Improved event logging for better debugging
- Moved stock data functionality to dedicated StockDataProvider
```

### Connection Management

- [x] Improve WebSocket connection management
  - [x] Refactor `UIConnectionManager` to use the registry
  - [x] Add connection tracking by agent and component
  - [x] Implement better error handling for disconnects
  - [x] Add reconnection support

- [x] Implement event broadcasting
  - [x] Add methods to broadcast events to all clients
  - [x] Add methods to send events to specific clients
  - [x] Add event queuing for disconnected clients

### Completed Work

The following work has been completed for Connection Management:

```
feat: Implement enhanced UI connection manager

- Created dedicated UIConnectionManager class with improved connection tracking
- Added component-specific connection tracking and message routing
- Implemented reconnection support with message queuing for disconnected clients
- Added periodic cleanup of disconnected clients
- Added event broadcasting to all clients or specific components
- Integrated with the application startup process
```

### Data Handling

- [x] Create modular data providers
  - [x] Move stock data functionality to a dedicated provider
  - [x] Create interface for data providers
  - [x] Implement caching for frequently requested data
  - [x] Add error handling and fallbacks

### Completed Work

The following work has been completed for Data Handling:

```
feat: Implement modular data providers with caching and error handling

- Created DataProvider base class with caching and error handling
- Created DataProviderRegistry for managing providers
- Implemented StockDataProvider with real data from yfinance
- Added fallback to mock data when real data is unavailable
- Created comprehensive tests for data providers
```

- [x] Implement request/response tracking
  - [x] Add request IDs for correlation
  - [x] Implement timeout handling
  - [x] Add retry logic for failed requests

### Completed Work

The following work has been completed for Request/Response Tracking:

```
feat: Implement request tracking system with timeout handling and retries

- Created RequestTracker class for tracking requests and responses
- Added request IDs for correlation between requests and responses
- Implemented timeout handling with configurable timeouts
- Added retry logic for failed requests with configurable max retries
- Integrated with the UI WebSocket handler for tracking component requests
- Added periodic cleanup of completed and error requests
- Integrated with the application startup and shutdown process
- Added comprehensive unit tests to verify functionality
```

Commit message:
```
feat(ui): Implement request tracking system with timeout handling and retries

This commit adds a robust request tracking system for UI components:
- Create RequestTracker class to manage request lifecycle
- Add unique request IDs for correlation between requests and responses
- Implement timeout handling with configurable timeouts using asyncio.wait_for
- Add retry logic for failed requests with configurable max retries
- Integrate with UI WebSocket handler for tracking component requests
- Add periodic cleanup of completed and error requests
- Integrate with application startup and shutdown process
- Add comprehensive unit tests to verify functionality

This implementation completes the "Implement request/response tracking" task
from the AGENT_UI_ROADMAP.md file and provides a reliable foundation for
handling asynchronous requests between the frontend and backend.
```

```
feat(ui): Replace DataProviders with direct Agent tool calls

This commit removes the DataProvider abstraction layer and replaces it with direct Agent tool calls:
- Remove StockDataProvider and VisualizationDataProvider classes
- Update UI components to directly use Agent tools via AgentRunner
- Modify StockChartComponent to use get_stock_history_tool from FinancialAnalysisAgent
- Update DataVisualizationComponent to use tools from relevant agents
- Add parsing logic in UI components to handle agent-formatted responses
- Update architecture diagrams to reflect the new direct agent-to-UI component relationship
- Add improved error handling for agent tool calls
- Update tests to use real agent implementations instead of mock data providers

This change simplifies the architecture by removing an unnecessary abstraction layer
and leverages the full capabilities of agents, including their reasoning abilities
and error handling. UI components now directly benefit from agent capabilities
like context-aware data formatting and intelligent error responses.
```

## Phase 3: Component Implementation

### Mock Data Strategy

- [x] Define mock data strategy
  - [x] Create abstract interfaces with no implementation
  - [x] Implement concrete classes with mock data in separate files
  - [x] Add clear TODOs and documentation for mock implementations
  - [x] Create plan for replacing mock data with real implementations

### Stock Chart Component Migration

- [x] Migrate stock chart to new architecture
  - [x] Create `StockChartComponent` interface (as part of VisualizationComponent)
  - [x] Create `MockStockChartComponent` implementation
  - [x] Implement required handlers with mock data
  - [x] Create real `StockChartComponent` implementation using data providers
  - [x] Update registration

### Completed Work

The following work has been completed for the Stock Chart Component Migration:

```
feat: Implement real StockChartComponent with data provider integration

- Created StockChartComponent that uses the StockDataProvider
- Implemented all required handlers with real data fetching
- Added proper error handling and caching
- Created comprehensive tests using real implementations
- Connected the component to the UI component registry
```

- [x] Add tests for stock chart component
  - [x] Test registration
  - [x] Test real data handling
  - [x] Test event handling
  - [x] Test component-provider integration

### Additional Components

- [x] Create research paper component
  - [x] Implement paper search functionality
  - [x] Implement citation visualization
  - [x] Implement note-taking features

### Completed Work

The following work has been completed for the Research Paper Component:

```
feat: Implement research paper component with Semantic Scholar API integration

- Created ResearchPaperProvider that uses the Semantic Scholar API for real data
- Implemented paper search functionality with filtering options
- Added paper details retrieval with metadata and abstracts
- Implemented citation and reference retrieval
- Created citation network visualization functionality
- Added note-taking features with tagging support
- Implemented comprehensive tests using real API data
- Connected the component to the research_supervisor and literature agents
```

- [x] Create data visualization component
  - [x] Implement chart types (bar, line, pie)
  - [x] Implement data filtering
  - [x] Implement export functionality

### Completed Work

The following work has been completed for the Data Visualization Component:

```
feat: Implement data visualization component with comprehensive charting capabilities

- Created VisualizationDataProvider for data processing, analysis, and generation
- Implemented support for multiple chart types (bar, line, pie, scatter, area, bubble, radar, polar, heatmap)
- Added data filtering and transformation capabilities
- Implemented data export functionality in various formats (CSV, JSON, etc.)
- Created comprehensive tests using real implementations
- Connected the component to the data_processing and financial_analysis agents
```

## Phase 4: Frontend Integration

### Agent-UI Association Model

- [x] Implement agent-UI association in frontend
  - [x] Create agent profile page with UI component options
  - [x] Enable switching between chat and specialized UI modes
  - [x] Implement context preservation between modes
  - [x] Add agent capability badges to indicate available UIs

- [x] Create agent UI capability discovery
  - [x] Implement API endpoint for agent UI capabilities (`/api/agents/{agent_id}/has-ui`)
  - [x] Add frontend capability detection and display
  - [x] Only show UI buttons for agents with UI components
  - [ ] Create UI suggestion system based on conversation context
  - [ ] Implement dynamic UI recommendation

### Completed Work

The following work has been completed for Agent UI Capability Discovery:

```
feat(ui): Only show UI buttons for agents with UI components

This commit adds the ability to detect which agents have UI components and only show UI buttons for those agents:
- Add new API endpoint `/api/agents/{agent_id}/has-ui` to check if an agent has UI components
- Update Agent interface to include hasUI property
- Modify useAgents hook to fetch hasUI information for each agent
- Update AgentSelector and ChatInterface components to only show UI buttons for agents with hasUI=true

This implementation improves the user experience by only showing UI buttons for agents that actually have UI components registered to them, providing a cleaner and more intuitive interface.
```

### UI Component Routing and Rendering

- [x] Design UI component routing architecture
  - [x] Define URL structure for agent UIs (e.g., `/agent-ui?agentId={agent_id}`)
  - [x] Create routing mechanism for component rendering
  - [ ] Implement component mounting/unmounting lifecycle
  - [ ] Add deep linking support for sharing specific UI states

- [x] Implement component container system
  - [x] Create flexible container component for hosting custom UIs
  - [ ] Implement component state persistence across route changes
  - [x] Add support for component communication with parent containers
  - [ ] Create responsive layouts for different screen sizes

### Completed Work

The following work has been completed for the Agent-UI Association and Component Routing:

```
feat(frontend): Implement agent UI frontend integration

This commit adds the initial frontend integration for agent UI components:
- Create agent-ui page and container components
- Enable switching between chat and specialized UI modes
- Add UI buttons to agent selector and chat interface
- Implement WebSocket connection management for UI components
- Set up routing mechanism for component rendering

Files created/modified:
- frontend/components/agent-ui/agent-ui-container.tsx: Main container for agent-specific UI components
- frontend/app/agent-ui/page.tsx: Page component for displaying agent UI
- frontend/components/agents/agent-selector.tsx: Updated to include UI button
- frontend/components/chat/chat-interface.tsx: Added button to switch to agent UI
- frontend/app/chat/page.tsx: Updated to handle navigation between chat and UI modes
```

- [ ] Add hybrid view options
  - [ ] Implement split views with chat and UI components
  - [ ] Create collapsible chat interface within UI views
  - [ ] Add contextual switching between views based on interaction
  - [ ] Implement shared context between chat and UI components

### Component Registry Updates

- [ ] Update frontend component registry
  - [ ] Align with backend registry structure
  - [ ] Implement dynamic component loading
  - [ ] Add error handling for missing components
  - [ ] Create component versioning support

- [ ] Implement component discovery
  - [ ] Create endpoint to list available components
  - [ ] Add component capability detection
  - [ ] Implement component filtering
  - [ ] Add component search functionality

### WebSocket Integration

- [x] Enhance WebSocket communication
  - [x] Create WebSocket connection management for UI components
  - [x] Implement message routing to appropriate component instances
  - [ ] Add reconnection and error handling logic
  - [ ] Implement request/response correlation with request IDs

- [ ] Improve real-time updates
  - [ ] Add support for server-initiated updates
  - [ ] Implement event broadcasting to relevant components
  - [ ] Create notification system for background updates
  - [ ] Add progress indicators for long-running operations

### Component Lifecycle Management

- [ ] Enhance component lifecycle management
  - [ ] Add initialization hooks
  - [ ] Add cleanup hooks
  - [ ] Implement state persistence
  - [ ] Create component activity logging

### UI/UX Improvements

- [ ] Update agent UI navigation
  - [ ] Create sidebar navigation for agent selection
  - [ ] Implement tabbed interface for multiple components
  - [ ] Add breadcrumb navigation for complex UIs
  - [ ] Create consistent header/footer across components

- [ ] Enhance component containers
  - [ ] Add more configuration options
  - [ ] Implement responsive sizing
  - [ ] Add transition animations
  - [ ] Improve accessibility
  - [ ] Create consistent styling across components

### Required Adjustments to Existing Implementation

- [ ] Update backend WebSocket handler
  - [ ] Modify to support new routing structure
  - [ ] Add support for hybrid view communication
  - [ ] Enhance error handling for component-specific errors

- [ ] Extend UI component base class
  - [ ] Add support for component state serialization
  - [ ] Implement methods for hybrid view integration
  - [ ] Add capability advertisement methods

## Phase 5: Documentation & Testing

### Documentation

- [ ] Create developer guide
  - [ ] Document component creation process
  - [ ] Document handler implementation
  - [ ] Document registration process
  - [ ] Provide examples

- [ ] Create API documentation
  - [ ] Document registry API
  - [ ] Document component API
  - [ ] Document WebSocket protocol
  - [ ] Document event types

### Testing

- [x] Implement unit tests
  - [x] Test registry functionality
  - [x] Test component base classes
  - [x] Test WebSocket handler
  - [x] Test data providers

### Completed Work

The following work has been completed for Testing:

```
feat: Implement real component-based testing for UI components

- Created TestComponent class for testing the UI component system
- Implemented simplified test file using real components instead of mocks
- Fixed method name inconsistencies in UI component system
- Added proper component registration with agents in tests
- Updated roadmap to reflect testing progress
- Verified all tests pass successfully
```

- [ ] Implement integration tests
  - [ ] Test end-to-end component registration
  - [ ] Test WebSocket communication
  - [ ] Test agent-component interaction
  - [ ] Test error scenarios

### Demo Components

- [ ] Create demonstration components
  - [ ] Simple text visualization
  - [ ] Interactive form
  - [ ] Data visualization
  - [ ] Multi-step wizard

- [ ] Create demo page
  - [ ] Showcase all demo components
  - [ ] Provide interactive examples
  - [ ] Include code snippets
  - [ ] Add documentation links

## Phase 6: Deployment & Monitoring

### Deployment

- [ ] Update Docker configuration
  - [ ] Ensure all dependencies are included
  - [ ] Configure environment variables
  - [ ] Set up volume mounts for components

- [ ] Create deployment documentation
  - [ ] Document required environment variables
  - [ ] Document configuration options
  - [ ] Document scaling considerations

### Monitoring

- [ ] Implement component usage tracking
  - [ ] Track component opens
  - [ ] Track user interactions
  - [ ] Track errors
  - [ ] Generate usage reports

- [ ] Add performance monitoring
  - [ ] Track WebSocket message latency
  - [ ] Track component render time
  - [ ] Track data fetch time
  - [ ] Implement alerting for issues

## Future Enhancements

- [ ] Component marketplace
  - [ ] Allow third-party component registration
  - [ ] Implement component versioning
  - [ ] Add component ratings and reviews
  - [ ] Create discovery interface

- [ ] Advanced component features
  - [ ] Inter-component communication
  - [ ] Persistent component state
  - [ ] User preference saving
  - [ ] Offline functionality

- [ ] Mobile support
  - [ ] Optimize components for mobile
  - [ ] Implement responsive design
  - [ ] Add touch interactions
  - [ ] Test on various devices
