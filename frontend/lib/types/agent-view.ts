import { Agent, Tool } from "./index";
import { ReactNode } from "react";

/**
 * Layout types supported by agent views
 */
export type ViewLayout = 'full' | 'split' | 'dashboard';

/**
 * Configuration for different layout types
 */
export interface LayoutConfig {
  sidebar?: {
    width: number;
    resizable?: boolean;
  };
  toolbar?: {
    position: 'top' | 'bottom';
    height: number;
  };
  grid?: {
    columns: number;
    rows: number;
  };
}

/**
 * Tool access interface
 */
export interface ToolAccess {
  [key: string]: (...args: any[]) => Promise<any>;
}

/**
 * Update system interface
 */
export interface UpdateSystem {
  subscribe: (channel: string, handler: (data: any) => void) => () => void;
  publish: (channel: string, data: any) => void;
}

/**
 * Props passed to all view components
 */
export interface AgentViewProps {
  agent: AgentWithView;
  tools: ToolAccess;
  updates: UpdateSystem;
}

/**
 * Base view component type
 */
export type ViewComponent<T = {}> = React.FC<T & AgentViewProps>;

/**
 * Agent view definition
 */
export interface AgentView {
  layout: ViewLayout;
  components: {
    main: ViewComponent;
    sidebar?: ViewComponent;
    toolbar?: ViewComponent;
    [key: string]: ViewComponent | undefined;
  };
  tools: string[];
  layoutConfig?: LayoutConfig;
}

/**
 * Extended agent type with view support
 */
export interface AgentWithView extends Agent {
  id: string;
  hasCustomView: boolean;
  customView?: {
    name: string;
    layout: ViewLayout;
    capabilities: string[];
  };
  tools?: Tool[];
}

/**
 * View event types
 */
export interface ViewEvent {
  type: string;
  data: any;
  channel?: string;
  timestamp: number;
}

/**
 * View message types
 */
export interface ViewMessage {
  role: "user" | "assistant" | "system";
  content: string;
  agentId: string;
  channel?: string;
  data?: any;
}
