import React, { useRef, useEffect, useState } from 'react';
import Editor, { Monaco } from '@monaco-editor/react';
import { Save, HelpCircle, Sparkles } from 'lucide-react';
import { useTheme } from 'next-themes';

interface CodeEditorProps {
  content: string;
  onChange: (content: string) => void;
  onSave: () => void;
  onExplain?: () => void;
  onImprove?: () => void;
  onGenerate?: () => void;
  isLoading: boolean;
  currentFile: string | null;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  content,
  onChange,
  onSave,
  onExplain,
  onImprove,
  onGenerate,
  isLoading,
  currentFile,
}) => {
  const editorRef = useRef<any>(null);
  const [language, setLanguage] = useState<string>('plaintext');
  const { theme } = useTheme();
  const [editorTheme, setEditorTheme] = useState<string>('vs');
  
  // Update editor theme when application theme changes
  useEffect(() => {
    setEditorTheme(theme === 'dark' ? 'vs-dark' : 'vs');
  }, [theme]);

  // Detect language based on file extension
  useEffect(() => {
    if (currentFile) {
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
        // Add more mappings as needed
      };
      
      setLanguage(languageMap[extension] || 'plaintext');
    } else {
      setLanguage('plaintext');
    }
  }, [currentFile]);

  // Handle editor mount
  const handleEditorDidMount = (editor: any, monaco: Monaco) => {
    editorRef.current = editor;
    
    // Add keyboard shortcut for save (Ctrl+S / Cmd+S)
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      onSave();
    });
  };

  // Handle content change
  const handleEditorChange = (value: string | undefined) => {
    onChange(value || '');
  };

  return (
    <div className="h-full w-full flex flex-col">
      <div className="p-2 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
        <h2 className="text-lg font-semibold truncate">
          {currentFile ? currentFile.split('/').pop() : 'No file selected'}
        </h2>
        <div className="flex space-x-2">
          {onExplain && (
            <button
              className="px-2 py-1 text-sm border rounded hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center"
              onClick={onExplain}
              disabled={!currentFile || isLoading || !content}
              title="Explain this code"
            >
              <HelpCircle className="h-4 w-4 mr-1" />
              Explain
            </button>
          )}
          {onImprove && (
            <button
              className="px-2 py-1 text-sm border rounded hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center"
              onClick={onImprove}
              disabled={!currentFile || isLoading || !content}
              title="Improve this code"
            >
              <Sparkles className="h-4 w-4 mr-1" />
              Improve
            </button>
          )}
          <button
            className="px-2 py-1 text-sm border rounded hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center"
            onClick={() => {
              if (onGenerate) {
                onGenerate();
              }
            }}
            disabled={!currentFile || isLoading}
            title="Generate code with AI assistance"
          >
            <svg 
              className="h-4 w-4 mr-1" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M12 3v19" />
              <path d="M5 8l7-5 7 5" />
              <path d="M5 16l7 5 7-5" />
            </svg>
            Generate
          </button>
          <button
            className="px-2 py-1 text-sm border rounded hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center"
            onClick={onSave}
            disabled={!currentFile || isLoading}
          >
            <Save className="h-4 w-4 mr-1" />
            Save
          </button>
        </div>
      </div>
      
      <div className="flex-grow">
        {!currentFile ? (
          <div className="flex justify-center items-center h-full text-gray-500">
            <p>Select a file to edit</p>
          </div>
        ) : isLoading ? (
          <div className="flex justify-center items-center h-full">
            <p>Loading...</p>
          </div>
        ) : (
          <Editor
            height="100%"
            language={language}
            value={content}
            onChange={handleEditorChange}
            onMount={handleEditorDidMount}
            theme={editorTheme}
            options={{
              minimap: { enabled: true },
              scrollBeyondLastLine: false,
              fontSize: 14,
              wordWrap: 'on',
              automaticLayout: true,
            }}
          />
        )}
      </div>
    </div>
  );
};

export default CodeEditor;
