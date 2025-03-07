# Mosaic Framework Architecture

This document provides a comprehensive overview of the Mosaic framework architecture, using the Financial Analysis agent and UI components as an example.

## System Architecture Diagram

```mermaid
graph TB
    %% Main Components
    User((User))
    Frontend[Frontend Application]
    Backend[Backend Server]
    Database[(Database)]
    LLM[Language Model]
    
    %% Frontend Components
    subgraph "Frontend (Next.js)"
        FrontendApp[App Router]
        WebSocketClient[WebSocket Client]
        UIComponents[UI Components]
        AgentUI[Agent UI]
        
        %% Financial UI Components
        subgraph "Financial UI Components"
            StockChart[Stock Chart Component]
            StockDataViz[Stock Data Visualization]
        end
        
        %% Context Providers
        subgraph "Context Providers"
            WebSocketContext[WebSocket Context]
            AgentUIContext[Agent UI Context]
        end
    end
    
    %% Backend Components
    subgraph "Backend (FastAPI)"
        WebSocketServer[WebSocket Server]
        UIComponentRegistry[UI Component Registry]
        AgentRegistry[Agent Registry]
        AgentRunner[Agent Runner]
        
        %% UI Components
        subgraph "UI Components"
            StockChartComponent[Stock Chart Component]
            StockDataVizComponent[Stock Data Visualization Component]
            DataVisualizationComponent[Data Visualization Component]
            VisualizationComponent[Visualization Component]
        end
        
        %% Agents
        subgraph "Agents"
            FinancialAnalysisAgent[Financial Analysis Agent]
            FinancialSupervisor[Financial Supervisor]
            
            %% Agent Tools
            subgraph "Financial Tools"
                GetStockPrice[Get Stock Price Tool]
                GetStockHistory[Get Stock History Tool]
                GetCompanyInfo[Get Company Info Tool]
                CalculateTechnicalIndicators[Calculate Technical Indicators Tool]
                GetStockComparison[Get Stock Comparison Tool]
            end
        end
    end
    
    %% External Services
    YFinance[YFinance API]
    
    %% Connections
    User --> Frontend
    Frontend <--> Backend
    Backend <--> Database
    Backend <--> LLM
    
    %% Frontend Connections
    FrontendApp --> UIComponents
    FrontendApp --> AgentUI
    AgentUI --> StockChart
    AgentUI --> StockDataViz
    WebSocketClient <--> WebSocketContext
    WebSocketContext --> AgentUIContext
    AgentUIContext --> StockChart
    AgentUIContext --> StockDataViz
    
    %% Backend Connections
    WebSocketServer <--> WebSocketClient
    WebSocketServer --> UIComponentRegistry
    UIComponentRegistry --> StockChartComponent
    UIComponentRegistry --> StockDataVizComponent
    StockChartComponent --> VisualizationComponent
    StockDataVizComponent --> DataVisualizationComponent
    DataVisualizationComponent --> VisualizationComponent
    
    %% Agent Connections
    WebSocketServer --> AgentRegistry
    AgentRegistry --> AgentRunner
    AgentRunner --> FinancialAnalysisAgent
    AgentRunner --> FinancialSupervisor
    FinancialAnalysisAgent --> GetStockPrice
    FinancialAnalysisAgent --> GetStockHistory
    FinancialAnalysisAgent --> GetCompanyInfo
    FinancialAnalysisAgent --> CalculateTechnicalIndicators
    FinancialAnalysisAgent --> GetStockComparison
    
    %% Data Provider Connections
    GetStockPrice --> YFinance
    GetStockHistory --> YFinance
    GetCompanyInfo --> YFinance
    
    %% UI Component to Agent Connections
    StockChartComponent -- "Uses Agent" --> AgentRunner
    StockDataVizComponent -- "Uses Agent" --> AgentRunner
    
    classDef frontend fill:#f9f,stroke:#333,stroke-width:2px;
    classDef backend fill:#bbf,stroke:#333,stroke-width:2px;
    classDef agent fill:#bfb,stroke:#333,stroke-width:2px;
    classDef database fill:#fb5,stroke:#333,stroke-width:2px;
    classDef external fill:#ddd,stroke:#333,stroke-width:2px;
    
    class FrontendApp,WebSocketClient,UIComponents,AgentUI,StockChart,StockDataViz,WebSocketContext,AgentUIContext frontend;
    class WebSocketServer,UIComponentRegistry,AgentRegistry,AgentRunner,StockChartComponent,StockDataVizComponent,DataVisualizationComponent,VisualizationComponent backend;
    class FinancialAnalysisAgent,FinancialSupervisor,GetStockPrice,GetStockHistory,GetCompanyInfo,CalculateTechnicalIndicators,GetStockComparison agent;
    class Database database;
    class YFinance,LLM external;
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend (React/Next.js)
    participant WebSocket as WebSocket Connection
    participant UIComponent as UI Component (Backend)
    participant AgentRunner as Agent Runner
    participant FinancialAgent as Financial Analysis Agent
    participant LLM as Language Model
    participant YFinance as YFinance API
    
    User->>Frontend: Interact with Stock Chart UI
    Frontend->>WebSocket: Send UI Event (get_stock_data)
    WebSocket->>UIComponent: Forward UI Event
    
    Note over UIComponent: Stock Chart Component
    
    UIComponent->>AgentRunner: Request Stock Data from Agent
    AgentRunner->>FinancialAgent: Run get_stock_history_tool
    FinancialAgent->>LLM: Generate Tool Parameters
    LLM-->>FinancialAgent: Return Parameters
    FinancialAgent->>YFinance: Fetch Stock Data
    YFinance-->>FinancialAgent: Return Raw Stock Data
    FinancialAgent->>LLM: Format Data Response
    LLM-->>FinancialAgent: Return Formatted Response
    FinancialAgent-->>AgentRunner: Return Formatted Stock Data
    
    AgentRunner-->>UIComponent: Return Agent Response
    Note over UIComponent: Parse Agent Response
    
    UIComponent-->>WebSocket: Send Data Response
    WebSocket-->>Frontend: Forward Data Response
    Frontend->>User: Update UI with Stock Data
    
    Note over Frontend,YFinance: Direct API calls are now replaced with Agent calls
```

## Component Hierarchy

```mermaid
classDiagram
    %% Base Classes
    class UIComponent {
        +component_id: str
        +name: str
        +description: str
        +register_handler()
        +handle_event()
    }
    
    class Agent {
        +name: str
        +model: LanguageModel
        +tools: List[Tool]
        +run_tool()
        +run_conversation()
    }
    
    %% UI Component Hierarchy
    class VisualizationComponent {
        +chart_types: List[str]
        +current_chart_type: str
        +handle_get_data()
        +handle_change_chart_type()
        +handle_export_data()
    }
    
    class DataVisualizationComponent {
        +handle_process_data()
        +handle_analyze_data()
        +handle_generate_data()
        +handle_get_chart_data()
        +_format_for_chart_type()
    }
    
    class StockChartComponent {
        +current_symbol: str
        +current_range: str
        +handle_get_stock_data()
        +handle_change_symbol()
        +handle_change_range()
        +_get_stock_data_from_agent()
        +_parse_stock_history_response()
    }
    
    class StockDataVisualizationComponent {
        +handle_get_stock_visualization_data()
        +handle_get_stock_comparison()
        +handle_get_stock_performance()
        +handle_get_market_distribution()
        +handle_get_stock_correlation()
        +_get_stock_comparison_data()
        +_parse_company_info_response()
    }
    
    %% Agent Hierarchy
    class BaseAgent {
        +name: str
        +model: LanguageModel
        +tools: List[Tool]
        +prompt: str
        +run_tool()
    }
    
    class FinancialAnalysisAgent {
        +get_stock_price_tool()
        +get_stock_history_tool()
        +get_company_info_tool()
        +calculate_technical_indicators_tool()
        +get_stock_comparison_tool()
    }
    
    class FinancialSupervisorAgent {
        +supervise_financial_analysis()
        +delegate_to_financial_agent()
    }
    
    %% Tool Hierarchy
    class Tool {
        +name: str
        +description: str
        +invoke()
    }
    
    class StockPriceTool {
        +invoke(symbol: str)
    }
    
    class StockHistoryTool {
        +invoke(symbol: str, period: str, interval: str)
    }
    
    class CompanyInfoTool {
        +invoke(symbol: str)
    }
    
    %% Relationships
    UIComponent <|-- VisualizationComponent
    VisualizationComponent <|-- StockChartComponent
    VisualizationComponent <|-- DataVisualizationComponent
    DataVisualizationComponent <|-- StockDataVisualizationComponent
    
    Agent <|-- BaseAgent
    BaseAgent <|-- FinancialAnalysisAgent
    BaseAgent <|-- FinancialSupervisorAgent
    
    Tool <|-- StockPriceTool
    Tool <|-- StockHistoryTool
    Tool <|-- CompanyInfoTool
    
    StockChartComponent --> FinancialAnalysisAgent : uses
    StockDataVisualizationComponent --> FinancialAnalysisAgent : uses
    
    FinancialAnalysisAgent --> StockPriceTool : has
    FinancialAnalysisAgent --> StockHistoryTool : has
    FinancialAnalysisAgent --> CompanyInfoTool : has
```

## Frontend Component Structure

```mermaid
graph TD
    %% Main Components
    App[App]
    Layout[Layout]
    Page[Page]
    
    %% Context Providers
    WebSocketProvider[WebSocket Provider]
    AgentUIProvider[Agent UI Provider]
    
    %% UI Components
    AgentUI[Agent UI]
    StockChart[Stock Chart]
    StockDataViz[Stock Data Visualization]
    
    %% Connections
    App --> Layout
    Layout --> WebSocketProvider
    WebSocketProvider --> AgentUIProvider
    AgentUIProvider --> Page
    Page --> AgentUI
    AgentUI --> StockChart
    AgentUI --> StockDataViz
    
    %% Component Details
    subgraph "Stock Chart Component"
        ChartControls[Chart Controls]
        ChartDisplay[Chart Display]
        SymbolSelector[Symbol Selector]
        RangeSelector[Range Selector]
    end
    
    subgraph "Stock Data Visualization Component"
        DataControls[Data Controls]
        DataDisplay[Data Display]
        ChartTypeSelector[Chart Type Selector]
        MetricSelector[Metric Selector]
        SymbolManager[Symbol Manager]
    end
    
    StockChart --> ChartControls
    StockChart --> ChartDisplay
    StockChart --> SymbolSelector
    StockChart --> RangeSelector
    
    StockDataViz --> DataControls
    StockDataViz --> DataDisplay
    StockDataViz --> ChartTypeSelector
    StockDataViz --> MetricSelector
    StockDataViz --> SymbolManager
    
    classDef component fill:#f9f,stroke:#333,stroke-width:2px;
    classDef provider fill:#bbf,stroke:#333,stroke-width:2px;
    classDef control fill:#bfb,stroke:#333,stroke-width:2px;
    
    class App,Layout,Page,AgentUI,StockChart,StockDataViz component;
    class WebSocketProvider,AgentUIProvider provider;
    class ChartControls,ChartDisplay,SymbolSelector,RangeSelector,DataControls,DataDisplay,ChartTypeSelector,MetricSelector,SymbolManager control;
```

## Agent-UI Interaction Flow

```mermaid
flowchart TD
    %% Main Components
    User((User))
    Frontend[Frontend]
    Backend[Backend]
    Agent[Financial Analysis Agent]
    LLM[Language Model]
    
    %% User Interactions
    User -->|1. Selects Stock Symbol| Frontend
    User -->|2. Selects Time Range| Frontend
    User -->|3. Selects Chart Type| Frontend
    
    %% Frontend Processing
    Frontend -->|4. Sends UI Event| Backend
    
    %% Backend Processing
    Backend -->|5. Routes to UI Component| UIComponent[Stock Chart Component]
    UIComponent -->|6. Requests Data| Agent
    
    %% Agent Processing
    Agent -->|7. Formats Request| LLM
    LLM -->|8. Returns Formatted Request| Agent
    Agent -->|9. Executes Tool| YFinance[YFinance API]
    YFinance -->|10. Returns Raw Data| Agent
    Agent -->|11. Formats Response| LLM
    LLM -->|12. Returns Formatted Response| Agent
    
    %% Response Flow
    Agent -->|13. Returns Formatted Data| UIComponent
    UIComponent -->|14. Parses Response| UIComponent
    UIComponent -->|15. Returns Structured Data| Backend
    Backend -->|16. Sends Data Response| Frontend
    Frontend -->|17. Updates UI| User
    
    %% Styling
    classDef user fill:#f96,stroke:#333,stroke-width:2px;
    classDef frontend fill:#f9f,stroke:#333,stroke-width:2px;
    classDef backend fill:#bbf,stroke:#333,stroke-width:2px;
    classDef agent fill:#bfb,stroke:#333,stroke-width:2px;
    classDef external fill:#ddd,stroke:#333,stroke-width:2px;
    
    class User user;
    class Frontend frontend;
    class Backend,UIComponent backend;
    class Agent agent;
    class LLM,YFinance external;
```

## Key Improvements in the New Architecture

1. **Agent-Driven Data Flow**: All data now flows through the Financial Analysis agent rather than directly accessing external APIs. This allows the agent to:
   - Apply its reasoning capabilities to the data
   - Format and structure the data appropriately
   - Provide additional context and insights
   - Handle errors gracefully with meaningful messages

2. **Decoupled Components**: The UI components are now decoupled from specific data providers, making them more flexible and reusable.

3. **Enhanced User Experience**: The agent can provide more context and insights about the data, improving the overall user experience.

4. **Consistent Data Format**: The agent ensures that data is consistently formatted, even when coming from different sources.

5. **Error Handling**: The agent can provide meaningful error messages and fallback options when data is unavailable.
