import React, { useState } from 'react';

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

interface ElementDetailsPanelProps {
  element: StoryElement | null;
  relationships: Relationship[];
  elements: Record<string, StoryElement>;
  onUpdateElement?: (elementId: string, updates: Partial<StoryElement>) => void;
  onAnalyzeRelationships?: (elementId: string) => Promise<void>;
  analysisResult?: any;
}

const ElementDetailsPanel: React.FC<ElementDetailsPanelProps> = ({
  element,
  relationships,
  elements,
  onUpdateElement,
  onAnalyzeRelationships,
  analysisResult
}) => {
  const [analysisLoading, setAnalysisLoading] = useState(false);

  // Handle analyze relationships button click
  const handleAnalyzeClick = async () => {
    if (!element || !onAnalyzeRelationships) return;
    
    try {
      setAnalysisLoading(true);
      await onAnalyzeRelationships(element.id);
    } catch (error) {
      console.error('Error analyzing relationships:', error);
    } finally {
      setAnalysisLoading(false);
    }
  };

  if (!element) {
    return (
      <div className="border rounded-lg p-4 h-full">
        <h3 className="text-lg font-semibold mb-2">Element Details</h3>
        <p className="text-gray-500 dark:text-gray-400">
          Select an element in the graph to view its details.
        </p>
      </div>
    );
  }

  // Get related elements
  const relatedElements = relationships.map(rel => {
    const isSource = rel.source === element.id;
    const relatedElementId = isSource ? rel.target : rel.source;
    const relatedElement = elements[relatedElementId];
    
    return {
      relationship: rel,
      element: relatedElement,
      direction: isSource ? 'outgoing' : 'incoming'
    };
  });

  // Element type badge color
  const typeBadgeColor = {
    character: 'bg-blue-100 text-blue-800',
    location: 'bg-green-100 text-green-800',
    event: 'bg-orange-100 text-orange-800'
  }[element.type] || 'bg-gray-100 text-gray-800';

  return (
    <div className="border rounded-lg p-4 h-full overflow-y-auto">
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold">{element.name || 'Unnamed Element'}</h3>
          <span className={`px-2 py-1 text-xs rounded-full ${typeBadgeColor}`}>
            {element.type}
          </span>
        </div>
        
        <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
          {element.description || 'No description available.'}
        </p>
        
        <div className="text-xs text-gray-500">ID: {element.id}</div>
        
        {/* Analyze Relationships Button */}
        {onAnalyzeRelationships && (
          <div className="mt-3">
            <button
              onClick={handleAnalyzeClick}
              disabled={analysisLoading}
              className="text-sm px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
            >
              {analysisLoading ? 'Analyzing...' : 'Analyze Relationships'}
            </button>
          </div>
        )}
      </div>
      
      {/* Analysis Results */}
      {analysisResult && (
        <div className="mb-4">
          <h4 className="text-md font-medium mb-2">Analysis Results</h4>
          <div className="bg-purple-50 dark:bg-purple-900/20 rounded p-3">
            <div className="mb-2">
              <span className="font-medium text-sm">Centrality: </span>
              <span className="text-sm">{analysisResult.centrality || 'N/A'}</span>
            </div>
            <div className="mb-2">
              <span className="font-medium text-sm">Significance: </span>
              <span className="text-sm">{analysisResult.insights?.significance || 'N/A'}</span>
            </div>
            <div>
              <span className="font-medium text-sm">Role: </span>
              <span className="text-sm">{analysisResult.insights?.role || 'N/A'}</span>
            </div>
          </div>
        </div>
      )}
      
      {/* Attributes section */}
      {element.attributes && Object.keys(element.attributes).length > 0 && (
        <div className="mb-4">
          <h4 className="text-md font-medium mb-2">Attributes</h4>
          <div className="bg-gray-50 dark:bg-gray-800 rounded p-2">
            {Object.entries(element.attributes).map(([key, value]) => (
              <div key={key} className="mb-1">
                <span className="font-medium text-sm">{key}: </span>
                <span className="text-sm">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Relationships section */}
      <div>
        <h4 className="text-md font-medium mb-2">Relationships ({relatedElements.length})</h4>
        {relatedElements.length === 0 ? (
          <p className="text-sm text-gray-500">No relationships found.</p>
        ) : (
          <div className="space-y-2">
            {relatedElements.map(({ relationship, element: relatedElement, direction }) => (
              <div key={relationship.id} className="bg-gray-50 dark:bg-gray-800 rounded p-2">
                <div className="flex items-center">
                  <div className="flex-1">
                    <div className="font-medium text-sm">
                      {direction === 'outgoing' ? (
                        <>
                          <span>{relationship.type}</span>
                          <span className="mx-1">→</span>
                          <span>{relatedElement?.name || 'Unknown Element'}</span>
                        </>
                      ) : (
                        <>
                          <span>{relatedElement?.name || 'Unknown Element'}</span>
                          <span className="mx-1">→</span>
                          <span>{relationship.type}</span>
                        </>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {relationship.description || 'No description'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ElementDetailsPanel;
