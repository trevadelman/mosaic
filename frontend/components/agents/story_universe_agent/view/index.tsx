"use client";

import React, { useState, useEffect, useRef } from 'react';
import { AgentView, AgentViewProps } from "@/lib/types/agent-view";
import StoryUniverseGraph from './components/StoryUniverseGraph';
import ElementDetailsPanel from './components/ElementDetailsPanel';
import ControlPanel from './components/ControlPanel';

// Define interfaces for story universe data
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

interface UpdateSystem {
  type?: 'clear' | 'update';
  content?: any;
}

// Main Story Universe View Component
const StoryUniverseViewComponent: React.FC<AgentViewProps & { updates?: UpdateSystem }> = ({ agent, tools, updates }) => {
  const [universe, setUniverse] = useState<StoryUniverseData | null>(null);
  const [selectedElementId, setSelectedElementId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  // Fetch the story universe data
  const fetchUniverse = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Call the get_story_universe tool
      const result = await tools.get_story_universe();
      
      // Sanitize and parse the result
      const sanitizedResult = typeof result === 'string' 
        ? result.replace(/([{,]\s*)([a-zA-Z0-9_]+)\s*:/g, '$1"$2":')  // Ensure property names are quoted
        : JSON.stringify(result);
      
      // Parse the sanitized result
      const universeData = JSON.parse(sanitizedResult);
      
      // Debug logging
      console.log("Fetched universe data:", universeData);
      
      // Validate and set universe data
      if (universeData && typeof universeData === 'object') {
        setUniverse({
          elements: universeData.elements || {},
          relationships: Array.isArray(universeData.relationships) ? universeData.relationships : []
        });
      } else {
        throw new Error('Invalid universe data structure');
      }
    } catch (err) {
      console.error('Error fetching story universe:', err);
      setError('Failed to load story universe data');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Clear state on mount and handle updates
  useEffect(() => {
    const init = async () => {
      setUniverse(null);
      setSelectedElementId(null);
      setIsLoading(false);
      setError(null);
      setAnalysisResult(null);
      await tools.reset_story_universe();
      await fetchUniverse();
    };

    if (updates?.type === 'clear') {
      init();
    } else {
      fetchUniverse();
    }
  }, [updates]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      setUniverse(null);
      setSelectedElementId(null);
      setIsLoading(false);
      setError(null);
      setAnalysisResult(null);
    };
  }, []);
  
  // Get selected element and its relationships
  const selectedElement = selectedElementId && universe?.elements[selectedElementId] || null;
  const elementRelationships = selectedElementId 
    ? universe?.relationships.filter(rel => 
        rel.source === selectedElementId || rel.target === selectedElementId
      ) || []
    : [];
  
  // Handle element selection
  const handleElementSelect = (elementId: string) => {
    setSelectedElementId(elementId);
  };
  
  // Handle element generation
  const handleGenerateElement = async (elementType: string, description: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      console.log(`Generating ${elementType} with description: ${description}`);
      
      // Call the generate_story_element tool
      const result = await tools.generate_story_element(elementType, description);
      
      // Sanitize and parse the result
      let elementData;
      if (typeof result === 'string') {
        const cleanResult = result
          .replace(/\n/g, '')
          .replace(/\s+/g, ' ')
          .trim();
        elementData = JSON.parse(cleanResult);
      } else {
        elementData = result;
      }
      console.log("Generated element data:", elementData);
      
      if (!elementData || elementData.error) {
        setError(`Error generating element: ${elementData?.error || 'Invalid response'}`);
        return;
      }
      
      // Fetch the updated universe data
      await fetchUniverse();
    } catch (err) {
      console.error('Error generating element:', err);
      setError('Failed to generate element');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle universe generation
  const handleGenerateUniverse = async (genre: string, numCharacters: number, numLocations: number, numEvents: number) => {
    try {
      setIsLoading(true);
      setError(null);
      
      console.log(`Generating story universe with genre: ${genre}, characters: ${numCharacters}, locations: ${numLocations}, events: ${numEvents}`);
      
      // Call the generate_story_universe tool
      const result = await tools.generate_story_universe(genre, numCharacters, numLocations, numEvents);
      
      try {
        // First try to parse the result
        let universeData;
        if (typeof result === 'string') {
          // Clean up any potential formatting issues
          const cleanResult = result
            .replace(/\n/g, '') // Remove newlines
            .replace(/\s+/g, ' ') // Normalize spaces
            .replace(/([{,]\s*)([a-zA-Z0-9_]+)\s*:/g, '$1"$2":') // Ensure property names are quoted
            .trim(); // Remove leading/trailing whitespace
          
          try {
            universeData = JSON.parse(cleanResult);
          } catch (parseError) {
            console.error('Initial parse failed, attempting to fix JSON:', parseError);
            // If initial parse fails, try more aggressive cleanup
            const sanitizedResult = cleanResult
              .replace(/'/g, '"') // Replace single quotes with double quotes
              .replace(/\\/g, '\\\\') // Escape backslashes
              .replace(/\u0000/g, '\\u0000') // Handle null bytes
              .replace(/[\u0000-\u001F\u007F-\u009F]/g, '') // Remove control characters
              .replace(/,\s*([}\]])/g, '$1') // Remove trailing commas
              .replace(/([{,])\s*([a-zA-Z0-9_]+?)\s*:/g, '$1"$2":') // Ensure property names are quoted
              .replace(/:\s*'([^']*?)'\s*(,|})/g, ':"$1"$2') // Convert single quoted values to double quotes
              .replace(/([^\\])"([^"]*?)"/g, '$1\\"$2\\"') // Escape unescaped double quotes
              .replace(/\}\s*\{/g, '},{') // Fix object array syntax
              .replace(/\}\s*,\s*\]/g, '}]') // Fix trailing comma in arrays
              .replace(/\}\s*,\s*\}/g, '}}'); // Fix trailing comma in objects
            
            try {
              universeData = JSON.parse(sanitizedResult);
            } catch (finalError) {
              const error = finalError as Error;
              console.error('Failed to parse JSON even after sanitization:', error);
              throw new Error('Invalid JSON structure: ' + error.message);
            }
          }
        } else {
          universeData = result;
        }
        
        console.log("Generated universe data:", universeData);
        
        if (!universeData || typeof universeData !== 'object') {
          throw new Error('Invalid universe data structure');
        }
        
        if (universeData.error) {
          setError(`Error generating universe: ${universeData.error}`);
          return;
        }
        
        // Ensure elements and relationships are properly structured
        const elements = universeData.elements && typeof universeData.elements === 'object' ? universeData.elements : {};
        const relationships = Array.isArray(universeData.relationships) ? universeData.relationships : [];
        
        // Validate element structure
        for (const [id, element] of Object.entries(elements)) {
          const typedElement = element as Partial<StoryElement>;
          if (!typedElement || !typedElement.id || !typedElement.type) {
            console.warn(`Invalid element structure for ID ${id}:`, element);
            delete elements[id];
          }
        }
        
        // Validate relationship structure
        const validRelationships = relationships.filter((rel: unknown) => {
          const typedRel = rel as Partial<Relationship>;
          const isValid = typedRel && typedRel.source && typedRel.target && typedRel.type;
          if (!isValid) {
            console.warn('Invalid relationship structure:', rel);
          }
          return isValid;
        }) as Relationship[];
        
        // Update the universe state with validated data
        setUniverse({
          elements,
          relationships: validRelationships
        });
      } catch (err) {
        console.error('Error parsing universe data:', err);
        setError(`Error parsing universe data: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error generating universe:', err);
      setError('Failed to generate universe');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle relationship creation
  const handleCreateRelationship = async (
    sourceId: string, 
    targetId: string, 
    relationshipType: string, 
    description: string
  ) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Call the create_relationship tool
      const result = await tools.create_relationship(sourceId, targetId, relationshipType, description);
      
      try {
        // Sanitize and parse the result
        let relationshipData;
        if (typeof result === 'string') {
          const cleanResult = result
            .replace(/\n/g, '')
            .replace(/\s+/g, ' ')
            .trim();
          relationshipData = JSON.parse(cleanResult);
        } else {
          relationshipData = result;
        }
        
        console.log("Created relationship data:", relationshipData);
        
        if (!relationshipData || relationshipData.error) {
          setError(`Error creating relationship: ${relationshipData?.error || 'Invalid response'}`);
          return;
        }
        
        // Fetch the updated universe data
        await fetchUniverse();
      } catch (err) {
        console.error('Error parsing relationship data:', err);
        setError(`Error creating relationship: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error creating relationship:', err);
      setError('Failed to create relationship');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle save universe
  const handleSaveUniverse = async (universeId?: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Call the save_universe tool
      const result = await tools.save_universe(universeId);
      
      // Parse and handle the save result
      let saveData;
      if (typeof result === 'string') {
        const cleanResult = result
          .replace(/\n/g, '')
          .replace(/\s+/g, ' ')
          .trim();
        saveData = JSON.parse(cleanResult);
      } else {
        saveData = result;
      }
      console.log("Save result:", saveData);
      
      if (!saveData || !saveData.success) {
        setError(saveData?.error || 'Failed to save universe');
        return;
      }
      
      // Show success message
      setError(saveData.message);
    } catch (err) {
      console.error('Error saving universe:', err);
      setError('Failed to save universe');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle load universe
  const handleLoadUniverse = async (universeId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Call the load_universe tool
      const result = await tools.load_universe(universeId);
      
      // Parse and handle the load result
      let loadData;
      if (typeof result === 'string') {
        const cleanResult = result
          .replace(/\n/g, '')
          .replace(/\s+/g, ' ')
          .trim();
        loadData = JSON.parse(cleanResult);
      } else {
        loadData = result;
      }
      console.log("Load result:", loadData);
      
      if (!loadData || !loadData.success) {
        setError(loadData?.error || 'Failed to load universe');
        return;
      }
      
      // Update the universe state
      setUniverse(loadData.universe);
      
      // Show success message
      setError(loadData.message);
    } catch (err) {
      console.error('Error loading universe:', err);
      setError('Failed to load universe');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle relationship analysis
  const handleAnalyzeRelationships = async (elementId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      setAnalysisResult(null);
      
      console.log(`Analyzing relationships for element ${elementId}`);
      
      // Call the analyze_relationships tool
      const result = await tools.analyze_relationships(elementId);
      
      try {
        // Sanitize and parse the result
        let analysisData;
        if (typeof result === 'string') {
          const cleanResult = result
            .replace(/\n/g, '')
            .replace(/\s+/g, ' ')
            .trim();
          analysisData = JSON.parse(cleanResult);
        } else {
          analysisData = result;
        }
        
        console.log("Analysis result:", analysisData);
        
        if (!analysisData || analysisData.error) {
          setError(`Error analyzing relationships: ${analysisData?.error || 'Invalid response'}`);
          return;
        }
        
        // Set the analysis result
        setAnalysisResult(analysisData);
      } catch (err) {
        console.error('Error parsing analysis data:', err);
        setError(`Error analyzing relationships: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }
      
    } catch (err) {
      console.error('Error analyzing relationships:', err);
      setError('Failed to analyze relationships');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full w-full p-4 flex flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-bold">Story Universe Explorer</h1>
        <p className="text-gray-500 dark:text-gray-400">
          Create and explore interconnected story elements and their relationships.
        </p>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-4 gap-4 flex-grow">
        {/* Left sidebar - Controls */}
        <div className="col-span-1">
          <ControlPanel 
            onGenerateElement={handleGenerateElement}
            onCreateRelationship={handleCreateRelationship}
            onGenerateUniverse={handleGenerateUniverse}
            onGenerateFromText={async (text: string) => {
              try {
                setIsLoading(true);
                await tools.generate_universe_from_text(text);
                await fetchUniverse();
              } catch (err) {
                console.error('Error generating universe from text:', err);
                setError('Failed to generate universe from text');
              } finally {
                setIsLoading(false);
              }
            }}
            onClear={async () => {
              try {
                setIsLoading(true);
                await tools.reset_story_universe();
                await fetchUniverse();
              } catch (err) {
                console.error('Error clearing universe:', err);
                setError('Failed to clear universe');
              } finally {
                setIsLoading(false);
              }
            }}
            elements={universe?.elements || {}}
            isLoading={isLoading}
            onSaveUniverse={handleSaveUniverse}
            onLoadUniverse={handleLoadUniverse}
          />
        </div>
        
        {/* Main content - Graph visualization */}
        <div className="col-span-2">
          <StoryUniverseGraph 
            data={universe}
            onElementSelect={handleElementSelect}
            isLoading={isLoading}
          />
        </div>
        
        {/* Right sidebar - Element details */}
        <div className="col-span-1">
          <ElementDetailsPanel 
            element={selectedElement}
            relationships={elementRelationships}
            elements={universe?.elements || {}}
            onAnalyzeRelationships={handleAnalyzeRelationships}
            analysisResult={analysisResult}
          />
        </div>
      </div>
    </div>
  );
};

// Export the view configuration
const StoryUniverseView: AgentView = {
  layout: 'full',
  components: {
    main: StoryUniverseViewComponent
  },
  tools: [
    'generate_story_element',
    'create_relationship',
    'get_story_universe',
    'get_element_details',
    'update_element',
    'generate_story_universe',
    'analyze_relationships',
    'reset_story_universe',
    'generate_universe_from_text',
    'save_universe',
    'load_universe'
  ]
};

export default StoryUniverseView;
