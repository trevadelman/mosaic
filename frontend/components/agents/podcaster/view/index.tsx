"use client";

import React, { useState } from 'react';
import { AgentView, AgentViewProps } from "@/lib/types/agent-view";
import { CreatorView } from './components/CreatorView';
import { ConversationView } from './components/ConversationView';

// Main Podcaster View Component
const PodcasterViewComponent: React.FC<AgentViewProps> = (props) => {
  const [activeTab, setActiveTab] = useState<'create' | 'talk'>('create');

  return (
    <div className="h-full w-full p-4 flex flex-col">
      {/* Header with Tabs */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold mb-4">Universal Podcaster</h1>
        <div className="border-b">
          <nav className="-mb-px flex gap-4">
            <button
              onClick={() => setActiveTab('create')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'create'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Create a Podcast
            </button>
            <button
              onClick={() => setActiveTab('talk')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'talk'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Talk to a Podcaster
            </button>
          </nav>
        </div>
      </div>

      {/* Description based on active tab */}
      <p className="text-gray-500 dark:text-gray-400 mb-4">
        {activeTab === 'create' 
          ? "Generate podcast-style audio content with customizable voices"
          : "Have a conversation with an AI podcaster - record your voice and get responses"}
      </p>

      {/* Main Content */}
      {activeTab === 'create' ? (
        <CreatorView {...props} />
      ) : (
        <ConversationView {...props} />
      )}
    </div>
  );
};

// Export the view configuration
const PodcasterView: AgentView = {
  layout: 'full',
  components: {
    main: PodcasterViewComponent
  },
  tools: [
    'generate_speech',
    'generate_content',
    'transcribe_audio'
  ]
};

export default PodcasterView;
