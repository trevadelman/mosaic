import React, { useState } from 'react';

interface CodeOperationModalProps {
  isVisible: boolean;
  onClose: () => void;
  onSubmit: (prompt: string) => Promise<void>;
  isLoading: boolean;
  title: string;
  description: string;
  submitLabel: string;
  defaultPrompt?: string;
}

const CodeOperationModal: React.FC<CodeOperationModalProps> = ({
  isVisible,
  onClose,
  onSubmit,
  isLoading,
  title,
  description,
  submitLabel,
  defaultPrompt = '',
}) => {
  const [prompt, setPrompt] = useState<string>(defaultPrompt);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }
    
    setError(null);
    
    try {
      await onSubmit(prompt);
      // Don't close the modal here, let the parent component handle it
    } catch (error) {
      console.error('Error in code operation:', error);
      setError('An error occurred while processing your request');
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 max-w-md w-full">
        <h2 className="text-xl font-semibold mb-2">{title}</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-4">{description}</p>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="prompt" className="block text-sm font-medium mb-1">
              Additional Instructions (Optional)
            </label>
            <textarea
              id="prompt"
              className="w-full border rounded-md p-2 h-32 text-sm dark:bg-gray-700 dark:border-gray-600"
              placeholder="Enter any specific instructions or requirements..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={isLoading}
            />
            {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
          </div>
          
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 dark:text-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={isLoading}
            >
              {isLoading ? 'Processing...' : submitLabel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CodeOperationModal;
