"use client";

import React, { useState, useEffect, useRef } from 'react';
import { AgentView, AgentViewProps } from "@/lib/types/agent-view";
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';
import GeneratedCodePreview from './components/GeneratedCodePreview';
import CodeGenerationModal from './components/CodeGenerationModal';
import LoadingOverlay from './components/LoadingOverlay';

// Main Code Editor View Component
const CodeEditorViewComponent: React.FC<AgentViewProps> = ({ agent, tools, updates }) => {
  const [currentFile, setCurrentFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generatedCode, setGeneratedCode] = useState<string>('');
  const [explanation, setExplanation] = useState<string>('');
  const [currentDirectory, setCurrentDirectory] = useState<string>('code-editor-working-dir');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isPreviewVisible, setIsPreviewVisible] = useState<boolean>(false);
  const [isGenerationModalVisible, setIsGenerationModalVisible] = useState<boolean>(false);
  const [previewType, setPreviewType] = useState<'code' | 'explanation' | 'improvement'>('code');
  
  // State for resizable panels
  const [sidebarWidth, setSidebarWidth] = useState<number>(33); // Percentage
  const [isResizing, setIsResizing] = useState<boolean>(false);
  const startPosition = useRef<number>(0);
  const startWidth = useRef<number>(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Clear messages after 3 seconds
  useEffect(() => {
    if (errorMessage || successMessage) {
      const timer = setTimeout(() => {
        setErrorMessage(null);
        setSuccessMessage(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [errorMessage, successMessage]);

  // Load file content when file changes
  useEffect(() => {
    if (currentFile) {
      loadFileContent(currentFile);
    } else {
      setFileContent('');
    }
  }, [currentFile]);
  
  // Handle mouse down on divider
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Set resizing state
    setIsResizing(true);
    
    // Store initial position and width
    startPosition.current = e.clientX;
    startWidth.current = sidebarWidth;
    
    // Add event listeners for dragging
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    // Add a class to the body to indicate resizing is in progress
    document.body.classList.add('resizing');
    
    // Disable text selection during resize
    document.body.style.userSelect = 'none';
  };

  // Handle mouse move while dragging
  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing || !containerRef.current) return;
    
    // Calculate the delta and new width
    const containerRect = containerRef.current.getBoundingClientRect();
    const containerWidth = containerRect.width;
    
    const delta = e.clientX - startPosition.current;
    const deltaPercent = (delta / containerWidth) * 100;
    
    // Calculate new width
    const newWidth = startWidth.current + deltaPercent;
    
    // Limit width to reasonable values (10% to 90%)
    if (newWidth >= 10 && newWidth <= 90) {
      setSidebarWidth(newWidth);
    }
  };

  // Handle mouse up after dragging
  const handleMouseUp = () => {
    // Reset resizing state
    setIsResizing(false);
    
    // Remove event listeners
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
    
    // Remove the resizing class from the body
    document.body.classList.remove('resizing');
    
    // Re-enable text selection
    document.body.style.userSelect = '';
  };

  // Clean up event listeners on unmount
  useEffect(() => {
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  // Get the API base URL from environment variables
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

  const loadFileContent = async (filePath: string) => {
    try {
      setIsLoading(true);
      console.debug(`Loading file content for: ${filePath}`);
      
      const response = await fetch(`${API_BASE_URL}/files/read?path=${encodeURIComponent(filePath)}`);
      
      if (!response.ok) {
        const text = await response.text();
        console.error('API Error Response:', text);
        setErrorMessage(`Error loading file: Server returned ${response.status}`);
        setFileContent('');
        return;
      }
      
      const data = await response.json();
      console.debug('API Response data:', data);
      
      if (data.error) {
        console.error(data.error);
        setErrorMessage(`Error loading file: ${data.error}`);
        setFileContent('');
      } else {
        setFileContent(data.content);
      }
    } catch (error) {
      console.error('Error loading file:', error);
      setErrorMessage('An unexpected error occurred while loading the file.');
      setFileContent('');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveFile = async () => {
    if (!currentFile) return;
    
    try {
      console.debug(`Saving file: ${currentFile}`);
      
      const response = await fetch(`${API_BASE_URL}/files/write?path=${encodeURIComponent(currentFile)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: fileContent }),
      });
      
      console.debug('API Response status:', response.status);
      
      if (!response.ok) {
        const text = await response.text();
        console.error('API Error Response:', text);
        setErrorMessage(`Error saving file: Server returned ${response.status}`);
        return;
      }
      
      const data = await response.json();
      console.debug('API Response data:', data);
      
      if (data.error) {
        console.error(data.error);
        setErrorMessage(`Error saving file: ${data.error}`);
      } else {
        setSuccessMessage(`Successfully saved ${currentFile}`);
      }
    } catch (error) {
      console.error('Error saving file:', error);
      setErrorMessage('An unexpected error occurred while saving the file.');
    }
  };

  const handleFileSelect = (filePath: string) => {
    setCurrentFile(filePath);
  };

  const handleDirectoryChange = (directoryPath: string) => {
    setCurrentDirectory(directoryPath);
    // We don't need to clear the current file anymore since the tree view
    // allows navigating directories without losing the current file selection
  };

  const handleContentChange = (newContent: string) => {
    setFileContent(newContent);
  };

  // Handle opening the code generation modal
  const handleOpenGenerationModal = () => {
    setIsGenerationModalVisible(true);
  };
  
  // Handle closing the code generation modal
  const handleCloseGenerationModal = () => {
    setIsGenerationModalVisible(false);
  };
  
  // Handle generating code from the modal
  const handleGenerateCodeFromModal = async (prompt: string): Promise<void> => {
    try {
      setIsGenerating(true);
      
      // Create a prompt that specifically asks for code generation
      let fullPrompt = prompt;
      
      // If there's a current file, include it in the prompt
      if (currentFile) {
        const fileExtension = currentFile.split('.').pop()?.toLowerCase() || '';
        fullPrompt = `Generate code for a ${fileExtension} file based on this request: ${prompt}. Please provide the complete code that I can save to ${currentFile}. Include an explanation of what the code does and how it works.`;
      } else {
        fullPrompt = `Generate code based on this request: ${prompt}. Please provide the complete code in a code block. Include an explanation of what the code does and how it works.`;
      }
      
      // Use the agent's tools to generate code
      console.log("Generating code with prompt:", fullPrompt);
      const result = await tools.generate_code_tool(fullPrompt);
      console.log("Generated code result:", result);
      
      // Set the full result as the generated code, preserving the explanation and code blocks
      setGeneratedCode(typeof result === 'string' ? result : String(result));
      
      // Also extract the code for the diff view
      let extractedCode = '';
      let explanation = '';
      
      if (typeof result === 'string') {
        // Look for code blocks in markdown format
        const codeBlockRegex = /```(?:python|javascript|typescript|java|cpp|csharp|html|css)?\s*([\s\S]*?)```/g;
        let match = codeBlockRegex.exec(result);
        
        if (match) {
          // Use the first code block found
          extractedCode = match[1].trim();
          
          // Everything else is the explanation
          explanation = result.replace(match[0], '').trim();
          setExplanation(explanation);
        } else {
          // If no code block found, use the entire result
          extractedCode = result;
        }
      } else {
        extractedCode = String(result);
      }
      
      return Promise.resolve();
    } catch (error) {
      console.error('Error generating code:', error);
      setErrorMessage('An unexpected error occurred while generating code.');
      return Promise.reject(error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  // Legacy handler for backward compatibility
  const handleGenerateCode = async (prompt: string) => {
    try {
      setIsGenerating(true);
      
      await handleGenerateCodeFromModal(prompt);
      
      // Show the preview
      setPreviewType('code');
      setIsPreviewVisible(true);
    } catch (error) {
      console.error('Error in legacy generate code handler:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  // Handle code explanation
  const handleExplainCode = async () => {
    if (!currentFile || !fileContent) return;
    
    try {
      // Set the preview type to explanation before starting the loading process
      setPreviewType('explanation');
      setIsGenerating(true);
      
      // Create a prompt that asks for code explanation
      const fileExtension = currentFile.split('.').pop()?.toLowerCase() || '';
      const prompt = `Please explain this ${fileExtension} code in detail. Return a JSON object with 'code' and 'explanation' properties. The 'code' should be the original code, and the 'explanation' should be a detailed explanation of how the code works:\n\n${fileContent}`;
      
      // Use the agent's explain_code_tool
      console.log("Explaining code with prompt:", prompt);
      const result = await tools.explain_code_tool(prompt);
      console.log("Code explanation result:", result);
      
      // Try to parse the result as JSON
      try {
        if (typeof result === 'string') {
          // Look for JSON in the result
          const jsonMatch = result.match(/```json\s*([\s\S]*?)\s*```/) || 
                           result.match(/\{[\s\S]*"code"[\s\S]*"explanation"[\s\S]*\}/);
          
          if (jsonMatch) {
            const jsonStr = jsonMatch[1] || jsonMatch[0];
            const parsedResult = JSON.parse(jsonStr);
            
            if (parsedResult.code && parsedResult.explanation) {
              setGeneratedCode(parsedResult.code);
              setExplanation(parsedResult.explanation);
              setPreviewType('explanation');
              setIsPreviewVisible(true);
              return;
            }
          }
        }
      } catch (jsonError) {
        console.error('Error parsing JSON from explanation result:', jsonError);
      }
      
      // If JSON parsing fails, use the entire result as the explanation
      setGeneratedCode(fileContent); // Keep the original code
      setExplanation(typeof result === 'string' ? result : String(result));
      setPreviewType('explanation');
      setIsPreviewVisible(true);
      
    } catch (error) {
      console.error('Error explaining code:', error);
      setErrorMessage('An unexpected error occurred while explaining the code.');
    } finally {
      setIsGenerating(false);
    }
  };
  
  // Handle code improvement
  const handleImproveCode = async () => {
    if (!currentFile || !fileContent) return;
    
    try {
      // Set the preview type to improvement before starting the loading process
      setPreviewType('improvement');
      setIsGenerating(true);
      
      // Create a prompt that asks for code improvement
      const fileExtension = currentFile.split('.').pop()?.toLowerCase() || '';
      const prompt = `Please improve this ${fileExtension} code. Optimize it, fix any bugs, and follow best practices. Return a JSON object with 'code' and 'explanation' properties. The 'code' should be the improved code, and the 'explanation' should explain what changes were made and why:\n\n${fileContent}`;
      
      // Use the agent's improve_code_tool
      console.log("Improving code with prompt:", prompt);
      const result = await tools.improve_code_tool(prompt);
      console.log("Code improvement result:", result);
      
      // Try to parse the result as JSON
      try {
        if (typeof result === 'string') {
          // Look for JSON in the result
          const jsonMatch = result.match(/```json\s*([\s\S]*?)\s*```/) || 
                           result.match(/\{[\s\S]*"code"[\s\S]*"explanation"[\s\S]*\}/);
          
          if (jsonMatch) {
            const jsonStr = jsonMatch[1] || jsonMatch[0];
            const parsedResult = JSON.parse(jsonStr);
            
            if (parsedResult.code && parsedResult.explanation) {
              setGeneratedCode(parsedResult.code);
              setExplanation(parsedResult.explanation);
              setPreviewType('improvement');
              setIsPreviewVisible(true);
              return;
            }
          }
        }
      } catch (jsonError) {
        console.error('Error parsing JSON from improvement result:', jsonError);
      }
      
      // If JSON parsing fails, extract code from the result
      let improvedCode = '';
      let explanation = '';
      
      if (typeof result === 'string') {
        // Look for code blocks in markdown format
        const codeBlockRegex = /```(?:python|javascript|typescript|java|cpp|csharp|html|css)?\s*([\s\S]*?)```/g;
        let match = codeBlockRegex.exec(result);
        
        if (match) {
          // Use the first code block found
          improvedCode = match[1].trim();
          
          // Everything else is the explanation
          explanation = result.replace(match[0], '').trim();
        } else {
          // If no code block found, use the entire result
          improvedCode = result;
        }
      } else {
        improvedCode = String(result);
      }
      
      // Set the improved code and show the preview
      setGeneratedCode(improvedCode);
      setExplanation(explanation);
      setPreviewType('improvement');
      setIsPreviewVisible(true);
      
    } catch (error) {
      console.error('Error improving code:', error);
      setErrorMessage('An unexpected error occurred while improving the code.');
    } finally {
      setIsGenerating(false);
    }
  };
  
  // Handle code preview actions
  const handleAcceptCode = async (code: string) => {
    // If coming from the modal, show the preview first
    if (isGenerationModalVisible) {
      // Extract code from the code parameter if it contains code blocks
      let extractedCode = code;
      let explanation = '';
      
      const codeBlockRegex = /```(?:.*?)?\n([\s\S]*?)```/;
      const match = code.match(codeBlockRegex);
      
      if (match && match[1]) {
        extractedCode = match[1].trim();
        explanation = code.replace(match[0], '').trim();
        setExplanation(explanation);
      }
      
      // Set the code for the preview
      setGeneratedCode(extractedCode);
      
      // Show the preview
      setPreviewType('code');
      setIsPreviewVisible(true);
      return;
    }
    
    // If the preview is visible, apply the code to the file
    if (isPreviewVisible) {
      // If there's a current file, update it with the accepted code
      if (currentFile) {
        setFileContent(code);
        
        // Save the file
        try {
          const response = await fetch(`${API_BASE_URL}/files/write?path=${encodeURIComponent(currentFile)}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: code }),
          });
          
          if (!response.ok) {
            const text = await response.text();
            console.error('API Error Response:', text);
            setErrorMessage(`Error saving file: Server returned ${response.status}`);
          } else {
            setSuccessMessage(`Generated code saved to ${currentFile}`);
          }
        } catch (error) {
          console.error('Error saving file:', error);
          setErrorMessage('An unexpected error occurred while saving the file.');
        }
      }
      
      // Close the preview
      setIsPreviewVisible(false);
    }
  };
  
  const handleRejectCode = () => {
    // Just close the preview without applying the code
    setIsPreviewVisible(false);
  };
  
  const handleClosePreview = () => {
    // Close the preview without applying the code
    setIsPreviewVisible(false);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Error and success messages */}
      {errorMessage && (
        <div className="p-2 bg-red-100 text-red-800 border-b border-red-200">
          {errorMessage}
        </div>
      )}
      {successMessage && (
        <div className="p-2 bg-green-100 text-green-800 border-b border-green-200">
          {successMessage}
        </div>
      )}
      
      <div ref={containerRef} className="h-full flex">
        {/* Sidebar with File Browser and Agent Prompt */}
        <div 
          className="border-r border-gray-200 dark:border-gray-800 overflow-hidden"
          style={{ width: `${sidebarWidth}%` }}
        >
          <Sidebar
            currentDirectory={currentDirectory}
            onDirectoryChange={handleDirectoryChange}
            onFileSelect={handleFileSelect}
            currentFile={currentFile}
            onGenerateCode={handleGenerateCode}
            isGenerating={isGenerating}
          />
        </div>
        
        {/* Resizable divider */}
        <div 
          className="resize-divider-horizontal"
          onMouseDown={handleMouseDown}
        />
        
        {/* Main Content with Code Editor */}
        <div 
          className="overflow-hidden"
          style={{ width: `${100 - sidebarWidth - 0.5}%` }}
        >
          <MainContent
            content={fileContent}
            onChange={handleContentChange}
            onSave={handleSaveFile}
            onExplain={handleExplainCode}
            onImprove={handleImproveCode}
            onGenerate={handleOpenGenerationModal}
            isLoading={isLoading}
            currentFile={currentFile}
          />
        </div>
      </div>
      
      {/* Generated Code Preview */}
      <GeneratedCodePreview
        originalCode={currentFile ? fileContent : ''}
        generatedCode={generatedCode}
        explanation={explanation}
        isVisible={isPreviewVisible}
        currentFile={currentFile}
        previewType={previewType}
        onAccept={handleAcceptCode}
        onReject={handleRejectCode}
        onClose={handleClosePreview}
      />
      
      {/* Loading Overlay */}
      <LoadingOverlay 
        isVisible={isGenerating} 
        message={
          (() => {
            // Determine the appropriate loading message based on the current operation
            if (previewType === 'explanation') {
              return 'Analyzing and explaining code...';
            } else if (previewType === 'improvement') {
              return 'Improving code...';
            } else {
              return 'Generating code...';
            }
          })()
        }
      />
      
      {/* Code Generation Modal */}
      <CodeGenerationModal
        isVisible={isGenerationModalVisible}
        onClose={handleCloseGenerationModal}
        onGenerate={handleGenerateCodeFromModal}
        onAccept={handleAcceptCode}
        isGenerating={isGenerating}
        generatedCode={generatedCode}
        currentFile={currentFile}
      />
    </div>
  );
};

// Export the view configuration
const CodeEditorView: AgentView = {
  layout: 'full',
  components: {
    main: CodeEditorViewComponent
  },
  tools: [
    'generate_code_tool',
    'explain_code_tool',
    'improve_code_tool'
  ]
};

export default CodeEditorView;
