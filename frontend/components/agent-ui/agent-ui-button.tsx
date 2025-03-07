/**
 * Agent UI Button Component
 * 
 * This component displays a button that can be used to open a custom UI component.
 * It's used in the chat interface to provide access to rich, interactive interfaces.
 */

"use client"

import React from 'react';
import { Button, ButtonProps } from '../ui/button';
import { useAgentUIComponents } from '../../lib/hooks/use-agent-ui-components';
import { ComponentRegistration } from '../../lib/types/agent-ui';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';

interface AgentUIButtonProps extends Omit<ButtonProps, 'onClick'> {
  /** The ID of the agent that provides the component */
  agentId: string;
  /** The ID of the component to open */
  componentId: string;
  /** Optional props to pass to the component */
  componentProps?: Record<string, any>;
  /** Optional tooltip text */
  tooltip?: string;
  /** Optional icon to display in the button */
  icon?: React.ReactNode;
  /** Optional label to display in the button */
  label?: string;
}

export const AgentUIButton: React.FC<AgentUIButtonProps> = ({
  agentId,
  componentId,
  componentProps,
  tooltip,
  icon,
  label,
  ...buttonProps
}) => {
  const { openComponent, isComponentOpen } = useAgentUIComponents({ agentId });
  
  // Handle button click
  const handleClick = () => {
    openComponent(componentId, componentProps);
  };
  
  // Check if the component is currently open
  const isOpen = isComponentOpen(componentId);
  
  // If there's a tooltip, wrap the button in a tooltip
  if (tooltip) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={handleClick}
              variant={isOpen ? 'default' : 'outline'}
              size="sm"
              className="flex items-center gap-2"
              {...buttonProps}
            >
              {icon}
              {label}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{tooltip}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }
  
  // Otherwise, just return the button
  return (
    <Button
      onClick={handleClick}
      variant={isOpen ? 'default' : 'outline'}
      size="sm"
      className="flex items-center gap-2"
      {...buttonProps}
    >
      {icon}
      {label}
    </Button>
  );
};

/**
 * Agent UI Button Group Component
 * 
 * This component displays a group of buttons for all available components for an agent.
 */
interface AgentUIButtonGroupProps {
  /** The ID of the agent */
  agentId: string;
  /** Optional filter function to filter components */
  filter?: (component: ComponentRegistration) => boolean;
  /** Optional function to get props for a component */
  getComponentProps?: (component: ComponentRegistration) => Record<string, any>;
  /** Optional function to get the icon for a component */
  getIcon?: (component: ComponentRegistration) => React.ReactNode;
  /** Optional function to get the label for a component */
  getLabel?: (component: ComponentRegistration) => string;
  /** Optional className for the container */
  className?: string;
}

export const AgentUIButtonGroup: React.FC<AgentUIButtonGroupProps> = ({
  agentId,
  filter,
  getComponentProps,
  getIcon,
  getLabel,
  className = 'flex flex-wrap gap-2',
}) => {
  const { availableComponents } = useAgentUIComponents({ agentId });
  
  // Filter components if a filter function is provided
  const filteredComponents = filter
    ? availableComponents.filter(filter)
    : availableComponents;
  
  // If there are no components, don't render anything
  if (filteredComponents.length === 0) {
    return null;
  }
  
  return (
    <div className={className}>
      {filteredComponents.map((component) => (
        <AgentUIButton
          key={component.id}
          agentId={agentId}
          componentId={component.id}
          componentProps={getComponentProps ? getComponentProps(component) : undefined}
          tooltip={component.description}
          icon={getIcon ? getIcon(component) : undefined}
          label={getLabel ? getLabel(component) : component.name}
        />
      ))}
    </div>
  );
};
