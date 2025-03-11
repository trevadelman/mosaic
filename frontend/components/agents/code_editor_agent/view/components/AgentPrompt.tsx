import React, { useState } from 'react';
import { Send } from 'lucide-react';

interface AgentPromptProps {
  onSubmit: (prompt: string) => void;
  isGenerating: boolean;
}

const AgentPrompt: React.FC<AgentPromptProps> = ({ onSubmit, isGenerating }) => {
  const [prompt, setPrompt] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && !isGenerating) {
      onSubmit(prompt);
      setPrompt('');
    }
  };

  return (
    <div className="h-full w-full p-2 flex flex-col">
      <form onSubmit={handleSubmit} className="flex flex-col h-full">
        <div className="mb-2 flex-shrink-0">
          <label htmlFor="prompt" className="text-sm font-medium">
            Ask the agent to generate or modify code
          </label>
        </div>
        <div className="flex flex-col flex-grow">
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Example: Generate a Python function to calculate Fibonacci numbers"
            className="flex-grow resize-none border rounded p-2 mb-2"
            disabled={isGenerating}
          />
          <div className="flex-shrink-0 flex justify-end">
            <button
              type="submit"
              className="px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center"
              disabled={!prompt.trim() || isGenerating}
            >
              {isGenerating ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating...
                </div>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Generate
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default AgentPrompt;
