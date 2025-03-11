import React, { useState, useEffect } from 'react';
import { Check, X, Edit, Copy, ArrowLeft, ArrowRight } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { useTheme } from 'next-themes';
import ReactMarkdown from 'react-markdown';

interface GeneratedCodePreviewProps {
  originalCode: string;
  generatedCode: string;
  explanation?: string;
  isVisible: boolean;
  currentFile: string | null;
  previewType: 'code' | 'explanation' | 'improvement';
  onAccept: (code: string) => void;
  onReject: () => void;
  onClose: () => void;
}

const GeneratedCodePreview: React.FC<GeneratedCodePreviewProps> = ({
  originalCode,
  generatedCode,
  explanation,
  isVisible,
  currentFile,
  previewType,
  onAccept,
  onReject,
  onClose,
}) => {
  const [modifiedCode, setModifiedCode] = useState<string>(generatedCode);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<'preview' | 'diff'>('preview');
  const { theme } = useTheme();
  const [editorTheme, setEditorTheme] = useState<string>('vs');
  
  // Update editor theme when application theme changes
  useEffect(() => {
    setEditorTheme(theme === 'dark' ? 'vs-dark' : 'vs');
  }, [theme]);
  
  // Update modified code when generatedCode prop changes
  useEffect(() => {
    setModifiedCode(generatedCode);
  }, [generatedCode]);
  
  if (!isVisible) {
    return null;
  }
  
  // Determine language based on file extension
  const getLanguage = () => {
    if (!currentFile) return 'plaintext';
    
    const extension = currentFile.split('.').pop()?.toLowerCase() || '';
    const languageMap: Record<string, string> = {
      js: 'javascript',
      jsx: 'javascript',
      ts: 'typescript',
      tsx: 'typescript',
      py: 'python',
      html: 'html',
      css: 'css',
      json: 'json',
      md: 'markdown',
      txt: 'plaintext',
    };
    
    return languageMap[extension] || 'plaintext';
  };
  
  const handleModifyClick = () => {
    setIsEditing(true);
  };
  
  const handleSaveModifications = () => {
    setIsEditing(false);
  };
  
  const handleCancelModifications = () => {
    setModifiedCode(generatedCode);
    setIsEditing(false);
  };
  
  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(modifiedCode);
  };
  
  const handleAccept = () => {
    onAccept(modifiedCode);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg w-4/5 h-4/5 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h2 className="text-lg font-semibold">
            {previewType === 'explanation' 
              ? (currentFile ? `Code Explanation for ${currentFile.split('/').pop()}` : 'Code Explanation')
              : previewType === 'improvement'
                ? (currentFile ? `Improved Code for ${currentFile.split('/').pop()}` : 'Improved Code')
                : (currentFile ? `Generated Code for ${currentFile.split('/').pop()}` : 'Generated Code')
            }
          </h2>
          <div className="flex space-x-2">
            {/* View mode toggle */}
            {currentFile && originalCode && (
              <div className="flex items-center mr-4 border rounded overflow-hidden">
                <button
                  className={`px-3 py-1 ${viewMode === 'preview' ? 'bg-blue-100 dark:bg-blue-900' : 'bg-transparent'}`}
                  onClick={() => setViewMode('preview')}
                  title="Preview mode"
                >
                  Preview
                </button>
                <button
                  className={`px-3 py-1 ${viewMode === 'diff' ? 'bg-blue-100 dark:bg-blue-900' : 'bg-transparent'}`}
                  onClick={() => setViewMode('diff')}
                  title="Diff mode"
                >
                  Diff
                </button>
              </div>
            )}
            
            {/* Action buttons */}
            <button
              className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
              onClick={handleCopyToClipboard}
              title="Copy to clipboard"
            >
              <Copy className="h-5 w-5" />
            </button>
            {isEditing ? (
              <>
                <button
                  className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-green-500"
                  onClick={handleSaveModifications}
                  title="Save modifications"
                >
                  <Check className="h-5 w-5" />
                </button>
                <button
                  className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-red-500"
                  onClick={handleCancelModifications}
                  title="Cancel modifications"
                >
                  <X className="h-5 w-5" />
                </button>
              </>
            ) : (
              <button
                className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-blue-500"
                onClick={handleModifyClick}
                title="Edit code"
              >
                <Edit className="h-5 w-5" />
              </button>
            )}
            <button
              className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-red-500"
              onClick={onClose}
              title="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
        
        {/* Content tabs for explanation and improvement types */}
        {(previewType === 'explanation' || previewType === 'improvement') && explanation && (
          <div className="border-b border-gray-200 dark:border-gray-700">
            <div className="flex">
              <button
                className={`px-4 py-2 ${viewMode === 'preview' ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-500'}`}
                onClick={() => setViewMode('preview')}
              >
                Code
              </button>
              <button
                className={`px-4 py-2 ${viewMode === 'diff' ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-500'}`}
                onClick={() => setViewMode('diff')}
              >
                {previewType === 'explanation' ? 'Explanation' : 'Changes'}
              </button>
            </div>
          </div>
        )}
        
        <div className="flex-grow overflow-hidden">
          {((previewType === 'explanation' || previewType === 'improvement') && viewMode === 'diff' && explanation) ? (
            // Explanation/Improvement view - show the explanation in markdown
            <div className="h-full overflow-y-auto p-4">
              <h3 className="mb-4">{previewType === 'explanation' ? 'Code Explanation' : 'Changes Made'}</h3>
              <div className="markdown-content prose dark:prose-invert max-w-none">
                <ReactMarkdown>
                  {explanation}
                </ReactMarkdown>
              </div>
            </div>
          ) : viewMode === 'preview' ? (
            // Preview mode - show just the generated code
            <Editor
              height="100%"
              language={getLanguage()}
              value={modifiedCode}
              onChange={(value) => isEditing && setModifiedCode(value || '')}
              theme={editorTheme}
              options={{
                readOnly: !isEditing,
                minimap: { enabled: true },
                scrollBeyondLastLine: false,
                fontSize: 14,
                wordWrap: 'on',
                automaticLayout: true,
              }}
            />
          ) : (
            // Diff mode - show side by side comparison
            <div className="flex h-full space-x-4">
              <div className="w-1/2 h-full flex flex-col">
                <div className="text-sm font-medium mb-2 text-gray-500">Original</div>
                <div className="flex-grow border rounded">
                  <Editor
                    height="100%"
                    language={getLanguage()}
                    value={originalCode}
                    theme={editorTheme}
                    options={{
                      readOnly: true,
                      minimap: { enabled: false },
                      scrollBeyondLastLine: false,
                      fontSize: 14,
                      wordWrap: 'on',
                      automaticLayout: true,
                    }}
                  />
                </div>
              </div>
              <div className="w-1/2 h-full flex flex-col">
                <div className="text-sm font-medium mb-2 text-gray-500">Generated</div>
                <div className="flex-grow border rounded">
                  <Editor
                    height="100%"
                    language={getLanguage()}
                    value={modifiedCode}
                    onChange={(value) => isEditing && setModifiedCode(value || '')}
                    theme={editorTheme}
                    options={{
                      readOnly: !isEditing,
                      minimap: { enabled: false },
                      scrollBeyondLastLine: false,
                      fontSize: 14,
                      wordWrap: 'on',
                      automaticLayout: true,
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-4">
          <button
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={onReject}
          >
            Reject
          </button>
          <button
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            onClick={handleAccept}
          >
            {currentFile ? 'Apply to File' : 'Accept'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default GeneratedCodePreview;
