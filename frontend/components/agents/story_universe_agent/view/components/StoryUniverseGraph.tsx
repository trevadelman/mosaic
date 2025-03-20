import React, { useCallback, useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';

// Dynamically import ForceGraph2D with no SSR
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full">
      <p>Loading graph visualization...</p>
    </div>
  )
});

interface StoryElement {
  id: string;
  type: string;
  name: string;
  description: string;
  attributes: Record<string, any>;
}

interface Relationship {
  id: string;
  source: string;
  target: string;
  type: string;
  description: string;
}

interface StoryUniverseData {
  elements: Record<string, StoryElement>;
  relationships: Relationship[];
}

interface StoryUniverseGraphProps {
  data: StoryUniverseData | null;
  onElementSelect?: (elementId: string) => void;
  isLoading?: boolean;
}

// Color mapping for element types
const typeColors = {
  character: '#3B82F6', // blue-500
  location: '#22C55E',  // green-500
  event: '#F97316',     // orange-500
  default: '#6B7280'    // gray-500
};

// Node size mapping for element types
const typeSizes = {
  character: 8,
  location: 10,
  event: 12,
  default: 6
};

const StoryUniverseGraph: React.FC<StoryUniverseGraphProps> = ({ 
  data, 
  onElementSelect,
  isLoading = false
}) => {
  const [graphData, setGraphData] = useState<{ nodes: any[], links: any[] }>({ nodes: [], links: [] });
  const [hoveredNode, setHoveredNode] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const graphRef = useRef<any>();
  const containerRef = useRef<HTMLDivElement>(null);
  const clickTimerRef = useRef<any>(null);
  const clickCountRef = useRef(0);
  
  // Convert story universe data to graph format
  useEffect(() => {
    if (!data) {
      setGraphData({ nodes: [], links: [] });
      return;
    }
    
    // Create nodes from elements
    const nodes = Object.values(data.elements).map(element => ({
      id: element.id,
      name: element.name || 'Unnamed',
      type: element.type,
      description: element.description,
      color: typeColors[element.type as keyof typeof typeColors] || typeColors.default,
      size: typeSizes[element.type as keyof typeof typeSizes] || typeSizes.default
    }));
    
    // Create links from relationships
    const links = data.relationships.map(rel => ({
      source: rel.source,
      target: rel.target,
      type: rel.type,
      description: rel.description
    }));
    
    setGraphData({ nodes, links });
  }, [data]);
  
  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (graphRef.current && containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        graphRef.current.width(width);
        graphRef.current.height(height);
      }
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // Handle node hover
  const handleNodeHover = useCallback((node: any) => {
    setHoveredNode(node);
    if (graphRef.current) {
      graphRef.current.nodeRelSize(node ? 8 : 6);
    }
  }, []);
  
  // Handle node click with double-click detection
  const handleNodeClick = useCallback((node: any) => {
    clickCountRef.current += 1;
    
    if (clickTimerRef.current) {
      clearTimeout(clickTimerRef.current);
    }
    
    clickTimerRef.current = setTimeout(() => {
      if (clickCountRef.current === 1) {
        // Single click
        setSelectedNode(node);
        if (onElementSelect) {
          onElementSelect(node.id);
        }
      } else if (clickCountRef.current === 2) {
        // Double click
        if (graphRef.current) {
          // Center view on node
          graphRef.current.centerAt(node.x, node.y, 1000);
          graphRef.current.zoom(2.5, 1000);
        }
      }
      clickCountRef.current = 0;
    }, 300); // 300ms click detection window
  }, [onElementSelect]);
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-100 dark:bg-gray-800 rounded-lg">
        <div className="text-center p-6">
          <p className="text-gray-500 dark:text-gray-400">Loading story universe...</p>
        </div>
      </div>
    );
  }
  
  if (!data || Object.keys(data.elements).length === 0) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-100 dark:bg-gray-800 rounded-lg">
        <div className="text-center p-6">
          <h3 className="text-xl font-semibold mb-2">Empty Story Universe</h3>
          <p className="text-gray-500 dark:text-gray-400">
            Use the controls to generate story elements and create relationships.
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <div ref={containerRef} className="relative w-full h-full bg-white dark:bg-gray-900 rounded-lg overflow-hidden">
      {/* Graph Legend */}
      <div className="absolute top-4 left-4 z-10 bg-white dark:bg-gray-800 p-2 rounded shadow-md">
        <div className="text-sm font-medium mb-1">Element Types</div>
        {Object.entries(typeColors).map(([type, color]) => (
          type !== 'default' && (
            <div key={type} className="flex items-center mb-1">
              <div
                className="w-3 h-3 rounded-full mr-2"
                style={{ backgroundColor: color }}
              />
              <span className="text-xs capitalize">{type}</span>
            </div>
          )
        ))}
        <div className="text-xs text-gray-500 mt-2">
          Double-click a node to zoom in
        </div>
      </div>
      
      {/* Node Tooltip */}
      {hoveredNode && (
        <div
          className="absolute z-10 bg-white dark:bg-gray-800 p-2 rounded shadow-md text-sm"
          style={{
            left: hoveredNode.x + 10,
            top: hoveredNode.y - 10,
            transform: 'translate(-50%, -100%)'
          }}
        >
          <div className="font-medium">{hoveredNode.name}</div>
          <div className="text-xs text-gray-500 capitalize">{hoveredNode.type}</div>
        </div>
      )}
      
      {/* Force Graph */}
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        nodeLabel="name"
        nodeColor="color"
        nodeVal="size"
        linkLabel="type"
        linkColor={() => '#9CA3AF'} // gray-400
        linkWidth={1}
        onNodeHover={handleNodeHover}
        onNodeClick={handleNodeClick}
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
          const size = node.size;
          const label = node.name;
          const fontSize = 12/globalScale;
          
          // Draw node
          ctx.beginPath();
          ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
          ctx.fillStyle = node.color;
          ctx.fill();
          
          // Draw label
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = 'black';
          ctx.fillText(label, node.x, node.y + size + fontSize);
        }}
        cooldownTicks={100}
        onEngineStop={() => {
          if (graphRef.current) {
            graphRef.current.zoomToFit(400);
          }
        }}
        width={containerRef.current?.clientWidth}
        height={containerRef.current?.clientHeight}
      />
    </div>
  );
};

export default StoryUniverseGraph;
