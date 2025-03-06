# MOSAIC Development Roadmap

## Phase 1: Project Setup and Infrastructure
- [x] **1.0 Initial Setup**
  - [x] Create mosaic directory
  - [x] Initialize git repository
  - [x] Create initial README.md
  - [x] Set up .gitignore
  - [x] Create directory structure

- [x] **1.1 Docker Configuration**
  - [x] Create docker directory
  - [x] Create Dockerfile.frontend
  - [x] Create Dockerfile.backend
  - [x] Create docker-compose.yml
  - [x] Test: Verify containers build and run
  - [x] Test: Verify volume mounting works
  - [x] Test: Verify container communication

- [x] **1.2 Frontend Foundation**
  - [x] Initialize Next.js project with TypeScript
  - [x] Install and configure shadcn/ui
  - [x] Set up dark theme
  - [x] Create basic layout with sidebar
  - [x] Test: Component rendering
  - [x] Test: Theme switching
  - [x] Test: Responsive layout

- [x] **1.3 Backend Foundation**
  - [x] Initialize FastAPI project
  - [x] Set up SQLite database
  - [x] Create basic API structure
  - [x] Configure CORS and middleware
  - [x] Test: API endpoints
  - [x] Test: Database connections
  - [x] Test: Error handling

## Phase 2: Core Agent System
- [x] **2.0 Base Agent Framework**
  - [x] Create base agent class
  - [x] Implement agent interface
  - [x] Set up agent registry
  - [x] Test: Agent registration
  - [x] Test: Base agent functionality

- [x] **2.1 Agent Factory System**
  - [x] Create agent factory class
  - [x] Implement agent creation logic
  - [x] Set up validation system
  - [x] Test: Agent creation
  - [x] Test: Validation rules

- [x] **2.2 Calculator Agent**
  - [x] Implement basic calculator agent
  - [x] Add operation handlers
  - [x] Create input parser
  - [x] Test: Basic operations
  - [x] Test: Error handling
  - [x] Test: Input validation

## Phase 3: Safety and Security
- [x] **3.0 Safety Vetting Agent**
  - [x] Create safety agent class
  - [x] Implement validation rules
  - [x] Set up approval system
  - [x] Test: Safety checks
  - [x] Test: Approval process
  - [x] Implement package installation security checks

- [x] **3.1 Private Writer Agent**
  - [x] Create writer agent class
  - [x] Implement file operations
  - [x] Set up security boundaries
  - [x] Test: File operations
  - [x] Test: Security constraints

## Phase 4: Frontend Features
- [x] **4.0 Chat Interface**
  - [x] Create chat components
  - [x] Implement WebSocket connection
  - [x] Add message handling
  - [x] Test: Real-time communication
  - [x] Test: Message rendering

- [x] **4.1 Agent Interaction UI**
  - [x] Create agent selection interface
  - [x] Add response visualization
  - [x] Implement error displays
  - [x] Test: User interactions
  - [x] Test: Error handling

- [x] **4.2 Real-time Communication Hardening**
  - [x] Create WebSocket Context Provider
    - [x] Implement global connection management
    - [x] Add connection state tracking
    - [x] Create message queue system
    - [x] Test: Connection state management
  
  - [x] Enhance Message Handling
    - [x] Update useChat hook with WebSocket context
    - [x] Implement message delivery confirmation
    - [x] Add offline message queueing
    - [x] Test: Message delivery reliability
  
  - [x] Improve Error Recovery
    - [x] Add connection heartbeat system
    - [x] Implement exponential backoff
    - [x] Create error boundary components
    - [x] Test: Recovery scenarios
  
  - [x] Performance Optimization
    - [ ] Add message batching (tbd)
    - [ ] Implement connection pooling (tbd)
    - [x] Optimize state updates
    - [x] Test: System under load

## Phase 5: Supervisor System
- [ ] **5.0 Research Supervisor Agent**
  - [x] Create research supervisor agent class
  - [x] Implement agent orchestration logic
  - [x] Design research-specific prompt
  - [x] Test: Basic research capabilities
  - [x] Test: Multi-agent orchestration

- [ ] **5.1 Supervisor UI Enhancements**
  - [ ] Update agent selection interface for supervisors
  - [ ] Implement agent hierarchy visualization
  - [ ] Add message attribution for sub-agents
  - [ ] Test: Supervisor agent selection
  - [ ] Test: Message attribution display

- [ ] **5.2 Enhanced Logging System**
  - [ ] Implement hierarchical logging
  - [ ] Add agent context to logs
  - [ ] Create log visualization for agent workflows
  - [ ] Test: Multi-agent logging
  - [ ] Test: Log visualization

- [x] **5.3 Agent Definition System**
  - [x] Design JSON schema for agent definitions
  - [x] Implement schema validation
  - [x] Create code generation system
  - [ ] Develop agent registration automation (partially implemented)
  - [x] Test: Schema validation
  - [x] Test: Code generation
  - [ ] Test: Agent registration

- [x] **5.4 Agent Sandbox Environment**
  - [x] Create isolated testing environment
  - [x] Implement agent loading in sandbox
  - [x] Add test suite for agent validation
  - [ ] Develop deployment pipeline from sandbox to production (partially implemented)
  - [x] Test: Sandbox isolation
  - [x] Test: Agent testing
  - [ ] Test: Deployment process

- [x] **5.5 Agent Creator Agent**
  - [x] Design agent creator tools
  - [x] Implement JSON template generation
  - [x] Create agent validation tools
  - [x] Build sandbox testing interface
  - [x] Develop deployment tools
  - [x] Test: Template generation
  - [x] Test: Agent validation
  - [ ] Test: End-to-end agent creation (partially implemented)

- [x] **5.6 Agent Creation UI**
  - [x] Implement JSON editor with schema validation
  - [x] Create visual tool builder
  - [x] Build prompt designer with templates
  - [x] Add sandbox testing interface
  - [x] Develop deployment workflow (partially implemented)
  - [x] Test: JSON editing
  - [x] Test: Tool building
  - [x] Test: Prompt design

- [x] **5.7 Agent Registration and Initialization Automation**
  - [x] Create dynamic agent discovery system
  - [x] Implement automatic agent registration on startup
  - [x] Develop plugin-based agent loading
  - [x] Refactor main.py to use dynamic agent registry
  - [x] Create agent metadata extraction system
  - [x] Test: Dynamic agent discovery
  - [x] Test: Automatic registration
  - [x] Test: Agent metadata extraction

- [x] **5.8 Agent API Endpoint Refactoring**
  - [x] Create dynamic API endpoint generation for agents
  - [x] Implement agent capability discovery
  - [x] Develop unified agent interface
  - [x] Extract agent routes from main.py
  - [x] Create agent-specific API modules
  - [x] Test: Dynamic endpoint generation
  - [x] Test: Agent capability discovery
  - [x] Test: API endpoint routing

## Phase 6: Database Integration and Multimodal Features
- [x] **6.0 SQLite Database Integration**
  - [x] Set up SQLite database models
  - [x] Implement database connection management
  - [x] Create migration system
  - [x] Update message storage to use database
  - [x] Add conversation persistence
  - [x] Implement conversation reset functionality
  - [x] Test: Database operations
  - [x] Test: Conversation persistence
  - [x] Test: Docker compatibility

  - [x] **6.0.1 Database-Driven Agent Metadata with JSON Template Integration**
    - [x] Create database models for agents, tools, capabilities, and relationships
    - [x] Implement JSON ↔ Database conversion functions
    - [x] Enhance agent generator to work with database records
    - [x] Update API to use database for agent operations
    - [x] Modify UI to display agent tools and relationships
    - [x] Implement CRUD operations for agent metadata
    - [x] Migrate existing agents to database structure
    - [x] Ensure compatibility with existing code generation
    - [x] Test: Database operations for agent metadata
    - [x] Test: Agent creation and modification through UI
    - [x] Test: Supervisor-agent relationship management
    - [x] Test: Migration of existing agents

 

- [x] **6.1 Vision Capabilities**
  - [x] Add image upload functionality to frontend
  - [x] Create backend endpoints for image handling
  - [x] Integrate with vision-capable models
  - [x] Update message components to display images
  - [x] Implement image processing utilities
  - [x] Test: Image upload and display
  - [x] Test: Vision model integration

- [x] **6.2 File Upload Processing**
  - [x] Add file upload functionality to frontend
  - [x] Create backend endpoints for file handling
  - [x] Implement file type detection
  - [x] Create specialized file processing agents:
    - [x] FileProcessingAgent for XLSX/CSV files
    - [ ] DocumentProcessingAgent for PDF files (planned)
    - [ ] MediaProcessingAgent for audio/video files (planned)
  - [x] Implement file processing tools:
    - [x] Tabular data extraction and formatting
    - [x] Data summary generation
    - [x] Basic statistical analysis
    - [ ] Advanced data visualization generation (planned)
  - [x] Create file processing supervisor agent:
    - [x] Design orchestration logic for file processing
    - [x] Implement file type routing system
    - [x] Create agent selection based on MIME types
    - [x] Develop preprocessing pipeline
  - [x] Integrate with WebSocket handler:
    - [x] Add preprocessing hooks before LLM processing
    - [x] Implement file processing status updates
    - [x] Create agent-to-agent communication for file data
  - [x] Update message components to display processed file content
  - [x] Test: File upload and processing
  - [x] Test: Excel file handling
  - [x] Test: End-to-end file processing pipeline

## Phase 7: Authentication and User Management

- [x] **7.0 Clerk Authentication Integration**
  - [x] Set up Clerk development environment and API keys
  - [x] Install and configure Clerk SDK
  - [x] Set up authentication routes
  - [x] Create protected routes middleware
  - [x] Implement user session management
  - [x] Configure Clerk webhook endpoints
  - [x] Implement auth state persistence
  - [x] Add auth error handling and recovery
  - [x] Test: Authentication flow
  - [x] Test: Session persistence
  - [x] Test: Protected routes
  - [x] Test: Error recovery

- [x] **7.1 Custom Authentication UI**
  - [x] Create auth layout wrapper
  - [x] Create login page
  - [x] Implement signup flow
  - [x] Add password reset functionality
  - [x] Create user profile page
  - [x] Add loading states for auth actions
  - [x] Implement auth redirects
  - [x] Add toast notifications for auth events
  - [x] Test: Login/signup UI
  - [x] Test: Form validation
  - [x] Test: Error handling
  - [x] Test: User experience

- [x] **7.2 User Data Association**
  - [x] Create database migration script for user_id columns
  - [x] Add user_id column to relevant database tables
  - [x] Add user preferences table
  - [x] Modify API endpoints to filter by user_id
  - [x] Update repository layer to include user context
  - [x] Implement multi-user data isolation
  - [x] Implement user settings management
  - [x] Add user data export/deletion capabilities
  - [x] Test: User data separation
  - [x] Test: Data privacy
  - [x] Test: API authorization
  - [x] Test: GDPR compliance

## Phase 8: Database Migration to Supabase

- [ ] **8.0 Supabase Setup**
  - [ ] Create Supabase project
  - [ ] Set up database schema
  - [ ] Configure authentication integration with Clerk
  - [ ] Set up environment variables
  - [ ] Test: Database connection
  - [ ] Test: Schema validation

- [ ] **8.1 ORM Migration**
  - [ ] Install Supabase Python client
  - [ ] Create database abstraction layer
  - [ ] Implement Supabase query builders
  - [ ] Update connection management
  - [ ] Test: CRUD operations
  - [ ] Test: Transaction handling

- [ ] **8.2 Repository Layer Updates**
  - [ ] Refactor repository classes for Supabase
  - [ ] Update service layer to use new repositories
  - [ ] Implement data migration scripts
  - [ ] Test: Repository operations
  - [ ] Test: Service layer functionality

- [ ] **8.3 Data Migration**
  - [ ] Create data export scripts for SQLite
  - [ ] Implement data import to Supabase
  - [ ] Verify data integrity
  - [ ] Test: Migration process
  - [ ] Test: Data consistency

## Phase 9: Documentation and Finalization

- [ ] **9.0 Documentation**
  - [ ] Create API documentation
  - [ ] Write development guides
  - [ ] Add inline code comments
  - [ ] Create usage examples

## Testing Strategy
Each checkpoint includes specific tests that must pass before moving forward:
1. Unit Tests: Individual component functionality
2. Integration Tests: Component interaction
3. End-to-End Tests: Full system functionality
4. Performance Tests: System efficiency
5. Security Tests: System safety

## Important Notes
1. **Reference Point**: Return to this roadmap at the start of each new task to ensure we're following the correct sequence.
2. **Testing First**: Write tests before implementing features when possible.
3. **Documentation**: Update documentation as we progress.
4. **Security**: Consider security implications at each step.

## Project Structure
```
mosaic/
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.frontend
│   └── Dockerfile.backend
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   ├── markdown.css
│   │   ├── agents/
│   │   │   └── page.tsx
│   │   ├── chat/
│   │   │   └── page.tsx
│   │   ├── community/
│   │   │   └── page.tsx
│   │   └── settings/
│   │       └── page.tsx
│   ├── components/
│   │   ├── theme-provider.tsx
│   │   ├── theme-toggle.tsx
│   │   ├── agents/
│   │   │   ├── agent-details.tsx
│   │   │   └── agent-selector.tsx
│   │   ├── chat/
│   │   │   ├── chat-input.tsx
│   │   │   ├── chat-interface.tsx
│   │   │   └── message.tsx
│   │   ├── sidebar/
│   │   │   └── sidebar.tsx
│   │   └── ui/
│   │       ├── accordion.tsx
│   │       ├── alert.tsx
│   │       ├── badge.tsx
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       ├── select.tsx
│   │       ├── separator.tsx
│   │       ├── tabs.tsx
│   │       ├── textarea.tsx
│   │       └── toast.tsx
│   └── lib/
│       ├── api.ts
│       ├── mock-data.ts
│       ├── types.ts
│       ├── utils.ts
│       ├── websocket.ts
│       ├── contexts/
│       │   └── websocket-context.tsx
│       └── hooks/
│           ├── use-agent-details.ts
│           ├── use-agents.ts
│           └── use-chat.ts
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── agent_api.py
│   │   ├── agent_discovery.py
│   │   ├── agent_runner.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── models.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent_generator.py
│   │   ├── base.py
│   │   ├── README.md
│   │   ├── internal/
│   │   │   ├── __init__.py
│   │   │   └── agent_generator.py
│   │   ├── regular/
│   │   │   ├── __init__.py
│   │   │   ├── browser_interaction.py
│   │   │   ├── calculator.py
│   │   │   ├── data_processing.py
│   │   │   ├── literature.py
│   │   │   ├── safety.py
│   │   │   ├── story_writer.py
│   │   │   ├── web_search.py
│   │   │   └── writer.py
│   │   └── supervisors/
│   │       ├── __init__.py
│   │       └── research_assistant.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── mosaic.db
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── migrations/
│   │       ├── create_agent_tables.py
│   │       └── migrate_agents_to_db.py
│   └── tests/
│       ├── __init__.py
│       ├── test_agent_creator_simple.py
│       ├── test_agent_creator.py
│       ├── test_agent_db.py
│       ├── test_agent_definition.py
│       ├── test_agent_sandbox.py
│       ├── test_calculator_direct.py
│       ├── test_calculator.py
│       ├── test_research_supervisor.py
│       ├── test_safety.py
│       └── test_writer.py
