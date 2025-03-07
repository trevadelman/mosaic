/**
 * Agent Modal Component
 * 
 * This component displays a custom UI component in a modal.
 * It's used by agents to provide rich, interactive interfaces.
 */

"use client"

import React, { useEffect, useState } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '../ui/sheet';
import { useAgentUI } from '../../lib/contexts/agent-ui-context';
import { AgentUIComponent } from '../../lib/types/agent-ui';
import { Button } from '../ui/button';
import { X } from 'lucide-react';

interface AgentModalProps {
  // Optional props
}

export const AgentModal: React.FC<AgentModalProps> = () => {
  const { activeComponentId, getComponent, closeComponentModal } = useAgentUI();
  const [activeComponent, setActiveComponent] = useState<AgentUIComponent | null>(null);
  const [isFullScreen, setIsFullScreen] = useState<boolean>(false);

  // Update active component when activeComponentId changes
  useEffect(() => {
    if (activeComponentId) {
      const component = getComponent(activeComponentId);
      setActiveComponent(component || null);
      
      // Set full screen mode based on component config
      if (component) {
        setIsFullScreen(component.modalConfig.size === 'full');
      }
    } else {
      setActiveComponent(null);
    }
  }, [activeComponentId, getComponent]);

  // If no active component, don't render anything
  if (!activeComponent) {
    return null;
  }

  // Get the component to render
  const ComponentToRender = activeComponent.component;
  
  // Determine the size class based on the modal config
  const getSizeClass = () => {
    switch (activeComponent.modalConfig.size) {
      case 'full':
        return 'w-screen h-screen max-w-none';
      case 'large':
        return 'w-[90vw] h-[90vh] max-w-6xl';
      case 'medium':
        return 'w-[80vw] h-[80vh] max-w-4xl';
      case 'small':
        return 'w-[60vw] h-[60vh] max-w-2xl';
      default:
        return 'w-[80vw] h-[80vh] max-w-4xl';
    }
  };

  // If full screen, render a custom full-screen modal
  if (isFullScreen) {
    return (
      <div className="fixed inset-0 z-50 bg-background flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-semibold">
            {activeComponent.props.title || 'Agent Interface'}
          </h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={closeComponentModal}
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>
        <div className="flex-1 overflow-auto p-0">
          <ComponentToRender {...activeComponent.props} />
        </div>
      </div>
    );
  }

  // Otherwise, render a Sheet component
  return (
    <Sheet open={!!activeComponentId} onOpenChange={(open) => !open && closeComponentModal()}>
      <SheetContent
        side="bottom"
        className={`${getSizeClass()} mx-auto rounded-t-lg overflow-hidden flex flex-col p-0`}
      >
        <SheetHeader className="px-6 py-4 border-b">
          <div className="flex items-center justify-between">
            <SheetTitle>
              {activeComponent.props.title || 'Agent Interface'}
            </SheetTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={closeComponentModal}
              aria-label="Close"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          {activeComponent.props.description && (
            <SheetDescription>
              {activeComponent.props.description}
            </SheetDescription>
          )}
        </SheetHeader>
        <div className="flex-1 overflow-auto p-0">
          <ComponentToRender {...activeComponent.props} />
        </div>
      </SheetContent>
    </Sheet>
  );
};
