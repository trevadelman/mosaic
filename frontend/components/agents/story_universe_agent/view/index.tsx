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
      
      // Parse the result
      let universeData;
      try {
        // First try to parse the content property if it exists
        const parsed = typeof result === 'string' ? JSON.parse(result) : result;
        universeData = parsed.content ? JSON.parse(parsed.content) : parsed;
      } catch (parseErr) {
        // If that fails, try to parse the result directly
        universeData = typeof result === 'string' ? JSON.parse(result) : result;
      }
      
      // Debug logging
      console.log("Fetched universe data:", universeData);
      
      setUniverse(universeData);
    } catch (err) {
      console.error('Error fetching story universe:', err);
      setError('Failed to load story universe data');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Fetch initial data and handle chat updates
  useEffect(() => {
    if (updates?.type === 'clear') {
      // Reset the story universe when chat is cleared
      tools.reset_story_universe().then(() => {
        fetchUniverse();
      }).catch(err => {
        console.error('Error resetting story universe:', err);
      });
    } else {
      fetchUniverse();
    }
  }, [updates]);
  
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
      
      // Parse the result
      const elementData = typeof result === 'string' ? JSON.parse(result) : result;
      console.log("Generated element data:", elementData);
      
      if (elementData.error) {
        setError(`Error generating element: ${elementData.error}`);
        return;
      }
      
      // Update the element with name and description from the LLM
      if (elementData.id) {
        // Extract name from description if not provided
        const name = description.split(',')[0].trim();
        
        // Create updates object
        const updates = {
          name: name,
          description: description
        };
        
        console.log(`Updating element ${elementData.id} with:`, updates);
        
        // Update the element with the extracted information
        try {
          const updateResult = await tools.update_element(elementData.id, JSON.stringify(updates));
          console.log("Update result:", updateResult);
        } catch (updateErr) {
          console.error('Error updating element:', updateErr);
        }
        
        // Fetch the updated universe data
        await fetchUniverse();
      }
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
      
      // Parse the result
      const universeData = typeof result === 'string' ? JSON.parse(result) : result;
      console.log("Generated universe data:", universeData);
      
      if (universeData.error) {
        setError(`Error generating universe: ${universeData.error}`);
        return;
      }
      
      // Update the universe elements with LLM-generated content
      const elementIds = Object.keys(universeData.elements || {});
      
      for (const elementId of elementIds) {
        const element = universeData.elements[elementId];
        
        // Generate a prompt for the LLM based on the element type and genre
        let prompt = "";
        if (element.type === "character") {
          prompt = `Create a detailed ${genre} character with a unique name, background, personality, and appearance.`;
        } else if (element.type === "location") {
          prompt = `Create a detailed ${genre} location with a unique name, description, atmosphere, and significance to the story.`;
        } else if (element.type === "event") {
          prompt = `Create a detailed ${genre} event with a unique name, description, participants, and consequences.`;
        }
        
        // Generate the element using the LLM
        try {
          console.log(`Generating detailed ${element.type} for ${genre} universe...`);
          const generatedResult = await tools.generate_story_element(element.type, prompt);
          const generatedData = typeof generatedResult === 'string' ? JSON.parse(generatedResult) : generatedResult;
          
          if (generatedData.error) {
            console.error(`Error generating ${element.type}:`, generatedData.error);
            continue;
          }
          
          // Update the original element with the generated content
          const updates = {
            name: `${element.type.charAt(0).toUpperCase() + element.type.slice(1)} ${elementId.substring(0, 4)}`,
            description: prompt
          };
          
          await tools.update_element(elementId, JSON.stringify(updates));
          
          // Now generate a more detailed update using the LLM
          const detailPrompt = `Create a detailed ${genre} ${element.type} named ${updates.name}. Include rich description, background, and characteristics.`;
          const detailedResult = await tools.generate_story_element(element.type, detailPrompt);
          
          // Extract the name from the first line or sentence of the description
          const detailedData = typeof detailedResult === 'string' ? JSON.parse(detailedResult) : detailedResult;
          if (!detailedData.error && detailedData.id) {
            // Get the detailed element
            const detailElement = await tools.get_element_details(detailedData.id);
            const detailData = typeof detailElement === 'string' ? JSON.parse(detailElement) : detailElement;
            
            if (!detailData.error && detailData.element) {
              // Use the detailed description to update the original element
              const detailedUpdates = {
                name: detailData.element.name || updates.name,
                description: detailData.element.description || updates.description,
                attributes: detailData.element.attributes || {}
              };
              
              await tools.update_element(elementId, JSON.stringify(detailedUpdates));
              
              // Delete the temporary element
              console.log(`Deleting temporary element ${detailedData.id}`);
              delete universeData.elements[detailedData.id];
            }
          }
        } catch (genErr) {
          console.error(`Error generating detailed content for ${element.type}:`, genErr);
        }
      }
      
      // Update relationships with LLM-generated descriptions
      for (const relationship of universeData.relationships) {
        try {
          const sourceElement = universeData.elements[relationship.source];
          const targetElement = universeData.elements[relationship.target];
          
          if (sourceElement && targetElement) {
            const sourceName = sourceElement.name || `${sourceElement.type} ${relationship.source.substring(0, 4)}`;
            const targetName = targetElement.name || `${targetElement.type} ${relationship.target.substring(0, 4)}`;
            
            const relationshipPrompt = `Describe a ${relationship.type} relationship between ${sourceName} (a ${sourceElement.type}) and ${targetName} (a ${targetElement.type}) in a ${genre} story.`;
            
            // Generate a detailed relationship description
            console.log(`Generating relationship description for ${sourceName} ${relationship.type} ${targetName}...`);
            
            // Update the relationship with a basic description
            relationship.description = relationshipPrompt;
          }
        } catch (relErr) {
          console.error('Error updating relationship:', relErr);
        }
      }
      
      // Fetch the updated universe data
      await fetchUniverse();
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
      
      // Parse the result
      const relationshipData = typeof result === 'string' ? JSON.parse(result) : result;
      
      if (relationshipData.error) {
        setError(`Error creating relationship: ${relationshipData.error}`);
        return;
      }
      
      // Fetch the updated universe data
      await fetchUniverse();
    } catch (err) {
      console.error('Error creating relationship:', err);
      setError('Failed to create relationship');
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
      
      // Parse the result
      const analysisData = typeof result === 'string' ? JSON.parse(result) : result;
      console.log("Analysis result:", analysisData);
      
      if (analysisData.error) {
        setError(`Error analyzing relationships: ${analysisData.error}`);
        return;
      }
      
      // Set the analysis result
      setAnalysisResult(analysisData);
      
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
    'generate_universe_from_text'
  ]
};

export default StoryUniverseView;
