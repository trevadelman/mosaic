import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Check } from 'lucide-react';

interface CodeGenerationModalProps {
  isVisible: boolean;
  onClose: () => void;
  onGenerate: (prompt: string) => Promise<void>;
  onAccept: (code: string) => void;
  isGenerating: boolean;
  generatedCode: string;
  currentFile: string | null;
}

const CodeGenerationModal: React.FC<CodeGenerationModalProps> = ({
  isVisible,
  onClose,
  onGenerate,
  onAccept,
  isGenerating,
  generatedCode,
  currentFile,
}) => {
  const [prompt, setPrompt] = useState<string>('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  // Reset state when modal is opened
  useEffect(() => {
    if (isVisible) {
      setPrompt('');
      setChatHistory([
        { 
          role: 'assistant' as const, 
          content: `I'll help you generate code for ${currentFile ? `"${currentFile.split('/').pop()}"` : 'a new file'}. What would you like to create?` 
        }
      ]);
    }
  }, [isVisible, currentFile]);
  
  // Scroll to bottom of chat when new messages are added
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory]);
  
  // Add generated code to chat history when it's received
  useEffect(() => {
    if (generatedCode && !isGenerating && chatHistory.length > 0 && chatHistory[chatHistory.length - 1].role !== 'assistant') {
      setChatHistory([...chatHistory, { role: 'assistant' as const, content: generatedCode }]);
    }
  }, [generatedCode, isGenerating]);
  
  const handleSubmit = async () => {
    if (!prompt.trim() || isSubmitting) return;
    
    // Add user message to chat history
    const updatedHistory = [...chatHistory, { role: 'user' as const, content: prompt }];
    setChatHistory(updatedHistory);
    
    // Clear prompt input
    setPrompt('');
    
    // Set submitting state
    setIsSubmitting(true);
    
    try {
      // Generate code based on the prompt
      await onGenerate(prompt);
    } catch (error) {
      console.error('Error generating code:', error);
      // Add error message to chat history
      setChatHistory([
        ...updatedHistory,
        { role: 'assistant' as const, content: 'Sorry, there was an error generating code. Please try again.' }
      ]);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (!isVisible) {
    return null;
  }
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg w-4/5 h-4/5 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h2 className="text-lg font-semibold">
            Generate Code {currentFile ? `for ${currentFile.split('/').pop()}` : ''}
          </h2>
          <button
            className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"
            onClick={onClose}
            title="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        
        <div className="flex-grow overflow-hidden flex flex-col">
          {/* Chat history */}
          <div className="flex-grow overflow-y-auto p-4">
            {chatHistory.map((message, index) => (
              <div 
                key={index} 
                className={`mb-4 ${message.role === 'user' ? 'text-right' : 'text-left'}`}
              >
                <div 
                  className={`inline-block p-3 rounded-lg ${
                    message.role === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                  }`}
                >
                  {message.role === 'assistant' && message.content.includes('```') ? (
                    <div>
                      <div className="whitespace-pre-wrap">
                        {message.content.split('```').map((part, i) => {
                          if (i % 2 === 0) {
                            return <span key={i}>{part}</span>;
                          } else {
                            // This is a code block
                            return (
                              <pre key={i} className="bg-gray-800 text-gray-100 p-2 rounded my-2 overflow-x-auto">
                                <code>{part}</code>
                              </pre>
                            );
                          }
                        })}
                      </div>
                      {message.content.includes('```') && (
                        <div className="mt-2 flex justify-end">
                          <button
                            className="px-2 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 flex items-center"
                            onClick={() => {
                              // Close the modal and show the preview with the full message content
                              onClose();
                              
                              // Extract code from the message for the diff view
                              const codeMatch = message.content.match(/```(?:.*?)?\n([\s\S]*?)```/);
                              if (codeMatch && codeMatch[1]) {
                                // Pass the extracted code to be applied to the file
                                onAccept(codeMatch[1]);
                              } else {
                                // If no code block found, use the entire message
                                onAccept(message.content);
                              }
                            }}
                          >
                            <Check className="h-3 w-3 mr-1" />
                            Preview Changes
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  )}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          
          {/* Input area */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex">
              <input
                type="text"
                className="flex-grow p-2 border rounded-l dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Describe the code you want to generate..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
                disabled={isGenerating || isSubmitting}
              />
              <button
                className="p-2 bg-blue-500 text-white rounded-r hover:bg-blue-600 flex items-center"
                onClick={handleSubmit}
                disabled={isGenerating || isSubmitting || !prompt.trim()}
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeGenerationModal;
