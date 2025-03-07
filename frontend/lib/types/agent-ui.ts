/**
 * Agent UI Component Types
 * 
 * This file defines the types and interfaces for the custom UI components
 * that can be used by agents to provide rich, interactive interfaces.
 */

import { ReactNode } from 'react';

/**
 * Size options for the modal
 */
export type ModalSize = 'full' | 'large' | 'medium' | 'small';

/**
 * Configuration for the modal
 */
export interface ModalConfig {
  /** Size of the modal */
  size: ModalSize;
  /** Array of panel IDs to display */
  panels: string[];
  /** Array of feature flags required by the component */
  features: string[];
  /** Whether the modal can be closed by the user */
  closable?: boolean;
  /** Custom CSS class names */
  className?: string;
}

/**
 * Agent UI Component interface
 * 
 * Defines the structure for custom UI components that can be
 * registered and used by agents.
 */
export interface AgentUIComponent {
  /** Unique identifier for the component */
  id: string;
  /** The React component to render */
  component: React.ComponentType<any>;
  /** Props to pass to the component */
  props: Record<string, any>;
  /** Configuration for the modal */
  modalConfig: ModalConfig;
}

/**
 * Extension to the AgentDefinition interface to include custom UI
 */
export interface AgentUIDefinition {
  /** Name of the component to use */
  component: string;
  /** Required features for the component */
  requiredFeatures: string[];
  /** Default props for the component */
  defaultProps?: Record<string, any>;
}

/**
 * UI Event types for WebSocket communication
 */
export type UIEventType = 'ui_update' | 'user_action' | 'data_request' | 'data_response';

/**
 * UI Event interface for WebSocket communication
 */
export interface UIEvent {
  /** Type of event */
  type: UIEventType;
  /** ID of the component that the event is for */
  component: string;
  /** Action to perform */
  action: string;
  /** Data associated with the event */
  data: any;
  /** Unique ID for the event, used for tracking responses */
  eventId?: string;
  /** Timestamp of the event */
  timestamp?: number;
}

/**
 * Component registration information
 */
export interface ComponentRegistration {
  /** Unique identifier for the component */
  id: string;
  /** Display name for the component */
  name: string;
  /** Description of the component */
  description: string;
  /** Agent ID that provides this component */
  agentId: string;
  /** Required features for the component */
  requiredFeatures: string[];
  /** Default modal configuration */
  defaultModalConfig: ModalConfig;
}
