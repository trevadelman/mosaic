# Building Orchestration Agents with LangChain and LangGraph

## Introduction

Orchestration agents are specialized AI systems designed to coordinate multiple sub-agents, each with distinct capabilities, to solve complex tasks. This document provides a comprehensive guide to building orchestration agents like the Research Assistant in the MOSAIC system, focusing on the LangChain and LangGraph tooling used and strategic approaches to designing effective orchestration systems.

## Core LangChain and LangGraph Components

### LangChain Components

1. **Language Models**
   ```python
   from langchain_core.language_models import LanguageModelLike
   ```
   - Provides a common interface for different language models
   - Enables model-agnostic agent design
   - Supports binding tools to models for enhanced capabilities

2. **Tools Framework**
   ```python
   from langchain_core.tools import BaseTool, tool
   ```
   - `BaseTool`: Base class for defining custom tools
   - `@tool` decorator: Simplifies tool creation with automatic schema generation
   - Enables agents to interact with external systems and APIs

3. **Messaging System**
   ```python
   from langchain_core.messages import AIMessage, ToolMessage
   ```
   - Structured message types for agent communication
   - `AIMessage`: Messages from the AI agent
   - `ToolMessage`: Messages containing tool execution results

### LangGraph Components

1. **Agent Creation**
   ```python
   from langgraph.prebuilt import create_react_agent
   ```
   - Creates ReAct (Reasoning + Acting) agents
   - Implements the reasoning-action loop for effective tool use
   - Handles parsing of model outputs and tool execution

2. **Workflow Management**
   ```python
   from langgraph.graph import StateGraph
   ```
   - Defines the flow between different agents
   - Manages state transitions based on agent outputs
   - Enables complex multi-agent workflows

3. **Agent Representation**
   ```python
   from langgraph.pregel import Pregel
   ```
   - Represents agents as computational graphs
   - Enables message passing between agents
   - Provides a unified interface for agent invocation

## Anatomy of an Orchestration Agent

### 1. Base Agent Structure

The MOSAIC system uses an abstract `BaseAgent` class that all agents inherit from:

```python
class BaseAgent(ABC):
    def __init__(
        self,
        name: str,
        model: LanguageModelLike,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Utility",
        capabilities: List[str] = None,
        icon: str = "🤖",
    ):
        # Initialization code...
        
    @abstractmethod
    def _get_default_prompt(self) -> str:
        # To be implemented by subclasses
        pass
    
    def create(self) -> Pregel:
        # Creates the agent using LangGraph
        if self.agent is None:
            # Bind tools to the model if supported
            model = self.model
            if hasattr(model, "bind_tools") and "parallel_tool_calls" in inspect.signature(model.bind_tools).parameters:
                model = model.bind_tools(self.tools, parallel_tool_calls=False)
            
            self.agent = create_react_agent(
                model=model,
                tools=self.tools,
                name=self.name,
                prompt=self.prompt
            )
        
        return self.agent
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Invokes the agent with the given state
        # Implementation...
```

### 2. Specialized Agents

Specialized agents implement specific capabilities:

```python
class WebSearchAgent(BaseAgent):
    def __init__(
        self,
        name: str = "web_search",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Specialized",
        capabilities: List[str] = None,
        icon: str = "🌐",
    ):
        # Create specialized tools
        web_search_tools = [
            search_web_tool,
            fetch_webpage_content_tool
        ]
        
        # Initialize with specialized configuration
        super().__init__(
            name=name,
            model=model,
            tools=web_search_tools + (tools or []),
            prompt=prompt,
            description=description or "Web Search Agent for searching the web and fetching webpage content",
            type=type,
            capabilities=capabilities or ["Web Search", "Content Retrieval"],
            icon=icon
        )
    
    def _get_default_prompt(self) -> str:
        # Specialized prompt for this agent type
        return (
            "You are a web research specialist with access to search engines and webpage content retrieval. "
            # More prompt content...
        )
```

### 3. Orchestration Agent (Supervisor)

The orchestration agent coordinates specialized agents:

```python
def create_research_supervisor(
    model: LanguageModelLike,
    output_mode: str = "full_history"
) -> StateGraph:
    # Register specialized agents if needed
    web_search = agent_registry.get("web_search")
    if web_search is None:
        web_search = register_web_search_agent(model)
    
    browser_interaction = agent_registry.get("browser_interaction")
    if browser_interaction is None:
        browser_interaction = register_browser_interaction_agent(model)
    
    # More agent registrations...
    
    # Define agent names to include
    agent_names = ["web_search", "browser_interaction", "data_processing", "literature"]
    
    # Create supervisor prompt
    prompt = (
        "You are a research coordinator managing a team of specialized agents:\n"
        "1. web_search: Use for general web searches and simple webpage content retrieval.\n"
        "2. browser_interaction: Use for JavaScript-heavy websites that require browser rendering.\n"
        # More prompt content...
    )
    
    # Create the supervisor
    supervisor = agent_registry.create_supervisor(
        model=model,
        agent_names=agent_names,
        prompt=prompt,
        name="research_supervisor",
        output_mode=output_mode
    )
    
    return supervisor.compile()
```

### 4. Agent Registry

The `AgentRegistry` manages all agents in the system:

```python
class AgentRegistry:
    def __init__(self):
        self.agents = {}
        self.logger = logging.getLogger("agent_registry")
    
    def register(self, agent: BaseAgent) -> None:
        # Register an agent
        self.agents[agent.name] = agent
    
    def get(self, name: str) -> Optional[BaseAgent]:
        # Get an agent by name
        return self.agents.get(name)
    
    def create_supervisor(
        self,
        model: LanguageModelLike,
        agent_names: List[str] = None,
        prompt: str = None,
        name: str = "supervisor",
        output_mode: str = "last_message"
    ) -> StateGraph:
        # Create a supervisor agent
        # Implementation...
```

## Tool Design for Orchestration

### 1. Specialized Tools

Each specialized agent has tools tailored to its domain:

```python
@tool
def search_web_tool(query: str, num_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo and return the results.
    
    Args:
        query: The search query
        num_results: Number of results to return (default: 5)
        
    Returns:
        A string containing search results with titles, snippets, and URLs
    """
    # Implementation...
```

### 2. Handoff Tools

Orchestration requires tools for delegating tasks to specialized agents:

```python
@tool
def transfer_to_web_search(query: str) -> str:
    """
    Transfer control to the web search agent to find information.
    
    Args:
        query: The search query to pass to the web search agent
        
    Returns:
        A string indicating successful transfer
    """
    # Implementation would handle the transfer of control
```

## Strategic Approach to Building Orchestration Agents

### 1. Agent Capability Analysis

Before building an orchestration agent, analyze the required capabilities:

1. **Task Decomposition**: Identify how complex tasks can be broken down
2. **Capability Mapping**: Determine which capabilities are needed for each subtask
3. **Agent Specialization**: Design specialized agents for each capability domain
4. **Coordination Requirements**: Define how agents need to interact

### 2. Prompt Engineering for Orchestration

The supervisor's prompt is critical for effective orchestration:

1. **Agent Introduction**: Clearly describe each specialized agent's capabilities
2. **Delegation Guidelines**: Provide rules for when to use each agent
3. **Coordination Instructions**: Explain how to synthesize information from multiple agents
4. **Error Handling**: Include strategies for handling agent failures
5. **Output Formatting**: Specify how to present the final results

Example:
```
You are a research coordinator managing a team of specialized agents:
1. web_search: Use for general web searches and simple webpage content retrieval.
2. browser_interaction: Use for JavaScript-heavy websites that require browser rendering.
3. data_processing: Use to extract and normalize product information from raw content.
4. literature: Use to find academic papers and articles related to products or technologies.

Your job is to coordinate these agents to gather comprehensive information about products, 
technologies, or companies. Break down research tasks and delegate to the appropriate agent. 
Synthesize the information they provide into a coherent response.

Important rules:
- When searching for current or latest information, avoid using specific years or dates in search queries.
- Exhaust all available tools and agents before giving up on a task. If one agent fails, try another approach.
- Only use factual information retrieved by the agents.
- If information cannot be found after trying all possible approaches, clearly state that and explain why.
- Never make up information or hallucinate details.
- Provide clear error reports when agents fail, but always try alternative approaches.
- Always attribute information to its source.
```

### 3. State Management Design

Design a state structure that supports orchestration:

1. **Conversation History**: Track all messages between agents
2. **Task Status**: Monitor the progress of each subtask
3. **Intermediate Results**: Store results from specialized agents
4. **Error States**: Track failures and recovery attempts
5. **Context Preservation**: Maintain context across agent handoffs

### 4. Workflow Design

Design the workflow between agents:

1. **Entry Point**: Define how tasks enter the system
2. **Routing Logic**: Determine how tasks are routed to specialized agents
3. **Handoff Mechanism**: Design how control transfers between agents
4. **Result Aggregation**: Define how results are collected and synthesized
5. **Exit Conditions**: Specify when the orchestration is complete

### 5. Testing and Evaluation

Develop a comprehensive testing strategy:

1. **Unit Testing**: Test each specialized agent independently
2. **Integration Testing**: Test interactions between agents
3. **End-to-End Testing**: Test complete workflows
4. **Failure Testing**: Test error handling and recovery
5. **Performance Testing**: Evaluate response times and resource usage

## Implementation Patterns

### 1. Agent Factory Pattern

Create agents dynamically based on requirements:

```python
def create_agent(agent_type: str, model: LanguageModelLike) -> BaseAgent:
    if agent_type == "web_search":
        return WebSearchAgent(model=model)
    elif agent_type == "browser_interaction":
        return BrowserInteractionAgent(model=model)
    # More agent types...
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")
```

### 2. Decorator Pattern for Tool Enhancement

Enhance tools with additional capabilities:

```python
def with_logging(tool_func):
    @functools.wraps(tool_func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {tool_func.__name__} with args: {args}, kwargs: {kwargs}")
        result = tool_func(*args, **kwargs)
        logger.info(f"{tool_func.__name__} returned: {result[:100]}...")
        return result
    return wrapper

@tool
@with_logging
def search_web_tool(query: str) -> str:
    # Implementation...
```

### 3. Strategy Pattern for Agent Selection

Select agents based on task requirements:

```python
class AgentSelector:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
    
    def select_agent(self, task: str) -> BaseAgent:
        if "search" in task.lower():
            return self.registry.get("web_search")
        elif "javascript" in task.lower() or "dynamic" in task.lower():
            return self.registry.get("browser_interaction")
        # More selection logic...
        else:
            return self.registry.get("default_agent")
```

### 4. Observer Pattern for Monitoring

Monitor agent activities:

```python
class AgentMonitor:
    def __init__(self):
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify(self, agent_name: str, event: str, data: Any):
        for observer in self.observers:
            observer.update(agent_name, event, data)
```

## Advanced Orchestration Techniques

### 1. Dynamic Agent Creation

Create specialized agents on-demand:

```python
def create_specialized_agent(task: str, model: LanguageModelLike) -> BaseAgent:
    # Analyze the task to determine required capabilities
    capabilities = analyze_task_requirements(task)
    
    # Create a custom agent with the required capabilities
    tools = []
    for capability in capabilities:
        tools.extend(get_tools_for_capability(capability))
    
    # Generate a specialized prompt
    prompt = generate_specialized_prompt(task, capabilities)
    
    # Create and return the agent
    return CustomAgent(
        name=f"specialized_{uuid.uuid4().hex[:8]}",
        model=model,
        tools=tools,
        prompt=prompt,
        capabilities=capabilities
    )
```

### 2. Hierarchical Orchestration

Create multi-level orchestration hierarchies:

```python
def create_hierarchical_supervisor(
    model: LanguageModelLike,
    domains: List[str]
) -> StateGraph:
    # Create domain-specific supervisors
    supervisors = []
    for domain in domains:
        supervisor = create_domain_supervisor(domain, model)
        supervisors.append(supervisor)
    
    # Create a top-level supervisor
    top_supervisor = create_top_supervisor(model, supervisors)
    
    return top_supervisor
```

### 3. Adaptive Routing

Route tasks based on agent performance:

```python
class AdaptiveRouter:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.performance_metrics = {}
    
    def route_task(self, task: str) -> BaseAgent:
        # Identify candidate agents
        candidates = self.identify_candidates(task)
        
        # Select the best performing agent
        best_agent = max(
            candidates,
            key=lambda agent: self.performance_metrics.get(agent.name, 0)
        )
        
        return best_agent
    
    def update_performance(self, agent_name: str, score: float):
        # Update performance metrics
        current = self.performance_metrics.get(agent_name, 0)
        self.performance_metrics[agent_name] = 0.9 * current + 0.1 * score
```

## Conclusion

Building effective orchestration agents with LangChain and LangGraph requires careful design of specialized agents, tools, prompts, and workflows. By following the strategic approach outlined in this document, you can create powerful multi-agent systems capable of solving complex tasks through coordinated collaboration.

The key to successful orchestration lies in:
1. Clear definition of agent capabilities
2. Effective task decomposition
3. Well-designed communication between agents
4. Robust error handling and recovery
5. Thoughtful state management

With these principles in mind, you can leverage the power of LangChain and LangGraph to build sophisticated orchestration agents that can tackle a wide range of complex tasks.
