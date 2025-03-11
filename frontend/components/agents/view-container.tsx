"use client";

import { AgentWithView, ViewLayout, LayoutConfig } from "@/lib/types/agent-view";
import { cn } from "@/lib/utils";
import { useEffect, useState, Children, ReactNode } from "react";

interface ViewContainerProps {
  agent: AgentWithView;
  children: ReactNode;
  layout: ViewLayout;
  config?: LayoutConfig;
  className?: string;
}

export function ViewContainer({
  agent,
  children,
  layout,
  config,
  className
}: ViewContainerProps) {
  // Track sidebar width for resizable layouts
  const [sidebarWidth, setSidebarWidth] = useState(
    config?.sidebar?.width || 320
  );
  
  // Track if currently resizing
  const [isResizing, setIsResizing] = useState(false);
  
  // Handle sidebar resize
  const handleResize = (e: MouseEvent) => {
    if (!isResizing) return;
    
    const newWidth = e.clientX;
    if (newWidth > 200 && newWidth < window.innerWidth - 400) {
      setSidebarWidth(newWidth);
    }
  };

  // Setup resize listeners
  useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', handleResize);
      window.addEventListener('mouseup', () => setIsResizing(false), { once: true });
      
      return () => {
        window.removeEventListener('mousemove', handleResize);
      };
    }
  }, [isResizing]);

  // Get children as array
  const childrenArray = Children.toArray(children);

  // Render different layouts
  switch (layout) {
    case 'split':
      return (
        <div className={cn("h-full flex overflow-hidden", className)}>
          {/* Sidebar */}
          <div 
            className="h-full border-r bg-background overflow-auto"
            style={{ width: sidebarWidth }}
          >
            {childrenArray[0]}
          </div>
          
          {/* Resize handle */}
          {config?.sidebar?.resizable && (
            <div 
              className={cn(
                "w-1 bg-border hover:bg-primary cursor-col-resize",
                isResizing && "bg-primary"
              )}
              onMouseDown={() => {
                setIsResizing(true);
                document.body.style.cursor = 'col-resize';
              }}
            />
          )}
          
          {/* Main content */}
          <div className="flex-1 h-full overflow-auto">
            {childrenArray[1]}
          </div>
        </div>
      );

    case 'dashboard':
      return (
        <div 
          className={cn(
            "grid gap-4 p-4 h-full overflow-auto",
            className
          )}
          style={{
            gridTemplateColumns: `repeat(${config?.grid?.columns || 2}, 1fr)`,
            gridTemplateRows: `repeat(${config?.grid?.rows || 2}, 1fr)`
          }}
        >
          {children}
        </div>
      );

    case 'full':
    default:
      return (
        <div className={cn("h-full flex flex-col overflow-hidden", className)}>
          {/* Top toolbar */}
          {config?.toolbar?.position === 'top' && (
            <div 
              className="border-b bg-background flex-shrink-0"
              style={{ height: config.toolbar.height }}
            >
              {childrenArray[0]}
            </div>
          )}
          
          {/* Main content */}
          <div className="flex-1 overflow-auto">
            {config?.toolbar?.position === 'top' ? childrenArray[1] : childrenArray[0]}
          </div>
          
          {/* Bottom toolbar */}
          {config?.toolbar?.position === 'bottom' && (
            <div 
              className="border-t bg-background flex-shrink-0"
              style={{ height: config.toolbar.height }}
            >
              {childrenArray[1]}
            </div>
          )}
        </div>
      );
  }
}
