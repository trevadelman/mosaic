import React, { useState } from 'react';

interface ControlPanelProps {
  onGenerateElement?: (elementType: string, description: string) => Promise<void>;
  onCreateRelationship?: (sourceId: string, targetId: string, relationshipType: string, description: string) => Promise<void>;
  onGenerateUniverse?: (genre: string, numCharacters: number, numLocations: number, numEvents: number) => Promise<void>;
  onGenerateFromText?: (text: string) => Promise<void>;
  onClear?: () => Promise<void>;
  onSaveUniverse?: (universeId?: string) => Promise<void>;
  onLoadUniverse?: (universeId: string) => Promise<void>;
  elements: Record<string, any>;
  isLoading?: boolean;
}

const ELEMENT_TYPES = ["character", "location", "event"];

const RELATIONSHIP_TYPES = [
  "knows", "related_to", "friends_with", "enemies_with", "loves", "hates",
  "works_at", "lives_in", "visited", "created", "destroyed", "participated_in",
  "owns", "leads", "follows", "betrayed", "saved", "located_in", "happened_at",
  "happened_before", "happened_after", "caused", "resulted_from"
];

const ControlPanel: React.FC<ControlPanelProps> = ({
  onGenerateElement,
  onCreateRelationship,
  onGenerateUniverse,
  onGenerateFromText,
  onClear,
  onSaveUniverse,
  onLoadUniverse,
  elements,
  isLoading = false
}) => {
  // State for element generation
  const [elementType, setElementType] = useState<string>("character");
  const [elementDescription, setElementDescription] = useState<string>("");
  const [showElementForm, setShowElementForm] = useState<boolean>(false);
  
  // State for relationship creation
  const [sourceId, setSourceId] = useState<string>("");
  const [targetId, setTargetId] = useState<string>("");
  const [relationshipType, setRelationshipType] = useState<string>("knows");
  const [relationshipDescription, setRelationshipDescription] = useState<string>("");
  const [showRelationshipForm, setShowRelationshipForm] = useState<boolean>(false);
  
  // State for universe generation
  const [genre, setGenre] = useState<string>("fantasy");
  const [numCharacters, setNumCharacters] = useState<number>(3);
  const [numLocations, setNumLocations] = useState<number>(2);
  const [numEvents, setNumEvents] = useState<number>(2);
  const [showUniverseForm, setShowUniverseForm] = useState<boolean>(false);
  
  // State for text upload
  const [storyText, setStoryText] = useState<string>("");
  const [showTextForm, setShowTextForm] = useState<boolean>(false);
  
  // State for universe management
  const [universeId, setUniverseId] = useState<string>("");
  const [showUniverseManagement, setShowUniverseManagement] = useState<boolean>(false);
  
  // Handle element generation
  const handleGenerateElement = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!onGenerateElement || !elementDescription.trim()) return;
    
    try {
      await onGenerateElement(elementType, elementDescription);
      
      // Reset form
      setElementDescription("");
      setShowElementForm(false);
    } catch (error) {
      console.error("Error generating element:", error);
    }
  };
  
  // Handle relationship creation
  const handleCreateRelationship = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!onCreateRelationship || !sourceId || !targetId) return;
    
    try {
      await onCreateRelationship(
        sourceId,
        targetId,
        relationshipType,
        relationshipDescription
      );
      
      // Reset form
      setRelationshipDescription("");
      setShowRelationshipForm(false);
    } catch (error) {
      console.error("Error creating relationship:", error);
    }
  };
  
  // Handle universe generation
  const handleGenerateUniverse = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!onGenerateUniverse) return;
    
    try {
      await onGenerateUniverse(genre, numCharacters, numLocations, numEvents);
      
      // Reset form
      setShowUniverseForm(false);
    } catch (error) {
      console.error("Error generating universe:", error);
    }
  };

  // Handle clear universe
  const handleClearUniverse = async () => {
    if (!onClear) return;
    
    try {
      await onClear();
      
      // Reset all forms
      setShowElementForm(false);
      setShowRelationshipForm(false);
      setShowUniverseForm(false);
    } catch (error) {
      console.error("Error clearing universe:", error);
    }
  };
  
  // Get element options for select
  const elementOptions = Object.entries(elements).map(([id, element]) => ({
    id,
    name: element.name || `Unnamed ${element.type}`,
    type: element.type
  }));

  return (
    <div className="border rounded-lg p-4 h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-2xl font-bold">Controls</h3>
        <button
          onClick={handleClearUniverse}
          disabled={isLoading}
          className="text-sm px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
        >
          Clear Universe
        </button>
      </div>
      
      {/* Element Generation */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-lg font-semibold">Generate Element</h4>
          <button
            className="text-sm px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            onClick={() => setShowElementForm(!showElementForm)}
            disabled={isLoading}
          >
            {showElementForm ? "Cancel" : "New"}
          </button>
        </div>
        
        {showElementForm && (
          <form onSubmit={handleGenerateElement} className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Element Type</label>
              <select
                value={elementType}
                onChange={(e) => setElementType(e.target.value)}
                className="w-full p-2 border rounded text-sm"
                disabled={isLoading}
              >
                {ELEMENT_TYPES.map(type => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea
                value={elementDescription}
                onChange={(e) => setElementDescription(e.target.value)}
                className="w-full p-2 border rounded text-sm h-20"
                placeholder={`Describe the ${elementType} you want to generate...`}
                disabled={isLoading}
              />
            </div>
            
            <button
              type="submit"
              className="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
              disabled={isLoading || !elementDescription.trim()}
            >
              {isLoading ? "Generating..." : "Generate"}
            </button>
          </form>
        )}
      </div>
      
      {/* Relationship Creation */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-lg font-semibold">Create Relationship</h4>
          <button
            className="text-sm px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
            onClick={() => setShowRelationshipForm(!showRelationshipForm)}
            disabled={isLoading || elementOptions.length < 2}
          >
            {showRelationshipForm ? "Cancel" : "New"}
          </button>
        </div>
        
        {elementOptions.length < 2 && !showRelationshipForm && (
          <p className="text-sm text-gray-500">
            You need at least two elements to create a relationship.
          </p>
        )}
        
        {showRelationshipForm && (
          <form onSubmit={handleCreateRelationship} className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Source Element</label>
              <select
                value={sourceId}
                onChange={(e) => setSourceId(e.target.value)}
                className="w-full p-2 border rounded text-sm"
                disabled={isLoading}
              >
                <option value="">Select source element</option>
                {elementOptions.map(element => (
                  <option key={element.id} value={element.id}>
                    {element.name} ({element.type})
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Relationship Type</label>
              <select
                value={relationshipType}
                onChange={(e) => setRelationshipType(e.target.value)}
                className="w-full p-2 border rounded text-sm"
                disabled={isLoading}
              >
                {RELATIONSHIP_TYPES.map(type => (
                  <option key={type} value={type}>
                    {type.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Target Element</label>
              <select
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                className="w-full p-2 border rounded text-sm"
                disabled={isLoading}
              >
                <option value="">Select target element</option>
                {elementOptions.map(element => (
                  <option key={element.id} value={element.id}>
                    {element.name} ({element.type})
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Description (Optional)</label>
              <textarea
                value={relationshipDescription}
                onChange={(e) => setRelationshipDescription(e.target.value)}
                className="w-full p-2 border rounded text-sm h-20"
                placeholder="Describe the relationship..."
                disabled={isLoading}
              />
            </div>
            
            <button
              type="submit"
              className="w-full py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
              disabled={isLoading || !sourceId || !targetId}
            >
              {isLoading ? "Creating..." : "Create Relationship"}
            </button>
          </form>
        )}
      </div>
      
      {/* Text Upload */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-lg font-semibold">Upload Story Text</h4>
          <button
            className="text-sm px-2 py-1 bg-indigo-500 text-white rounded hover:bg-indigo-600 disabled:opacity-50"
            onClick={() => setShowTextForm(!showTextForm)}
            disabled={isLoading}
          >
            {showTextForm ? "Cancel" : "New"}
          </button>
        </div>
        
        {showTextForm && (
          <form onSubmit={async (e) => {
            e.preventDefault();
            if (!onGenerateFromText || !storyText.trim()) return;
            
            try {
              await onGenerateFromText(storyText);
              setStoryText("");
              setShowTextForm(false);
            } catch (error) {
              console.error("Error generating from text:", error);
            }
          }} className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Story Text</label>
              <textarea
                value={storyText}
                onChange={(e) => setStoryText(e.target.value)}
                className="w-full p-2 border rounded text-sm h-40"
                placeholder="Paste your story text here..."
                disabled={isLoading}
              />
            </div>
            
            <button
              type="submit"
              className="w-full py-2 bg-indigo-500 text-white rounded hover:bg-indigo-600 disabled:opacity-50"
              disabled={isLoading || !storyText.trim()}
            >
              {isLoading ? "Generating..." : "Generate Universe from Text"}
            </button>
          </form>
        )}
      </div>
      
      {/* Universe Management */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-lg font-semibold">Universe Management</h4>
          <button
            className="text-sm px-2 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:opacity-50"
            onClick={() => setShowUniverseManagement(!showUniverseManagement)}
            disabled={isLoading}
          >
            {showUniverseManagement ? "Cancel" : "Manage"}
          </button>
        </div>
        
        {showUniverseManagement && (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Universe ID</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={universeId}
                  onChange={(e) => setUniverseId(e.target.value)}
                  placeholder="Enter universe ID to save/load"
                  className="flex-1 p-2 border rounded text-sm"
                  disabled={isLoading}
                />
                <button
                  onClick={() => onSaveUniverse?.(universeId)}
                  disabled={isLoading}
                  className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:opacity-50"
                >
                  Save
                </button>
              </div>
            </div>
            
            <div>
              <button
                onClick={() => onSaveUniverse?.()}
                disabled={isLoading}
                className="w-full py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:opacity-50"
              >
                Quick Save
              </button>
              <p className="text-xs text-gray-500 mt-1">
                Save with auto-generated ID based on timestamp
              </p>
            </div>
            
            <div>
              <button
                onClick={() => onLoadUniverse?.(universeId)}
                disabled={isLoading || !universeId.trim()}
                className="w-full py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:opacity-50"
              >
                Load Universe
              </button>
            </div>
          </div>
        )}
      </div>
      
      {/* Universe Generation */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-lg font-semibold">Generate Story Universe</h4>
          <button
            className="text-sm px-2 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
            onClick={() => setShowUniverseForm(!showUniverseForm)}
            disabled={isLoading}
          >
            {showUniverseForm ? "Cancel" : "New"}
          </button>
        </div>
        
        {showUniverseForm && (
          <form onSubmit={handleGenerateUniverse} className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Genre</label>
              <select
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                className="w-full p-2 border rounded text-sm"
                disabled={isLoading}
              >
                <option value="fantasy">Fantasy</option>
                <option value="sci-fi">Science Fiction</option>
                <option value="mystery">Mystery</option>
                <option value="romance">Romance</option>
                <option value="horror">Horror</option>
                <option value="historical">Historical</option>
                <option value="adventure">Adventure</option>
              </select>
            </div>
            
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-sm font-medium mb-1">Characters</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={numCharacters}
                  onChange={(e) => setNumCharacters(parseInt(e.target.value))}
                  className="w-full p-2 border rounded text-sm"
                  disabled={isLoading}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Locations</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={numLocations}
                  onChange={(e) => setNumLocations(parseInt(e.target.value))}
                  className="w-full p-2 border rounded text-sm"
                  disabled={isLoading}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Events</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={numEvents}
                  onChange={(e) => setNumEvents(parseInt(e.target.value))}
                  className="w-full p-2 border rounded text-sm"
                  disabled={isLoading}
                />
              </div>
            </div>
            
            <div className="pt-2">
              <button
                type="submit"
                className="w-full py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
                disabled={isLoading}
              >
                {isLoading ? "Generating..." : "Generate Universe"}
              </button>
              <p className="text-xs text-gray-500 mt-1">
                This will create a complete story universe with the specified elements and relationships between them.
              </p>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ControlPanel;
