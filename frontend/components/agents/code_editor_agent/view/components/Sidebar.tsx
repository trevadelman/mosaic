import React, { useState } from 'react';
import FileTreeView from './FileTreeView';
import { Plus, X, File, Folder, RefreshCw } from 'lucide-react';
import { 
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator
} from "@/components/ui/dropdown-menu";

interface SidebarProps {
  currentDirectory: string;
  onDirectoryChange: (directoryPath: string) => void;
  onFileSelect: (filePath: string) => void;
  currentFile: string | null;
  onGenerateCode: (prompt: string) => void;
  isGenerating: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({
  currentDirectory,
  onDirectoryChange,
  onFileSelect,
  currentFile,
  onGenerateCode,
  isGenerating,
}) => {
  const [showCreateFileForm, setShowCreateFileForm] = useState<boolean>(false);
  const [showCreateDirForm, setShowCreateDirForm] = useState<boolean>(false);
  const [newFileName, setNewFileName] = useState<string>('');
  const [newDirName, setNewDirName] = useState<string>('');
  const [newFileContent, setNewFileContent] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [selectedDirectory, setSelectedDirectory] = useState<string>(currentDirectory);
  const [refreshKey, setRefreshKey] = useState<number>(0);

  // Get the API base URL from environment variables
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

  // Clear messages after 3 seconds
  React.useEffect(() => {
    if (errorMessage || successMessage) {
      const timer = setTimeout(() => {
        setErrorMessage(null);
        setSuccessMessage(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [errorMessage, successMessage]);

  const handleCreateFile = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newFileName) {
      setErrorMessage('File name cannot be empty.');
      return;
    }
    
    try {
      const filePath = getFilePath(selectedDirectory, newFileName);
      console.debug(`Creating file: ${filePath}`);
      
      const response = await fetch(`${API_BASE_URL}/files/create?path=${encodeURIComponent(filePath)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: newFileContent }),
      });
      
      console.debug('API Response status:', response.status);
      
      if (!response.ok) {
        const text = await response.text();
        console.error('API Error Response:', text);
        setErrorMessage(`Error creating file: Server returned ${response.status}`);
        return;
      }
      
      const data = await response.json();
      console.debug('API Response data:', data);
      
      if (data.error) {
        console.error(data.error);
        setErrorMessage(`Error creating file: ${data.error}`);
      } else {
        setSuccessMessage(`Successfully created ${newFileName}`);
        
        // Select the new file
        onFileSelect(filePath);
        
        // Reset form
        setNewFileName('');
        setNewFileContent('');
        setShowCreateFileForm(false);
      }
    } catch (error) {
      console.error('Error creating file:', error);
      setErrorMessage('An unexpected error occurred while creating the file.');
    }
  };

  const handleCreateDirectory = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newDirName) {
      setErrorMessage('Directory name cannot be empty.');
      return;
    }
    
    try {
      // Create a directory by creating a temporary file inside it and then deleting it
      const dirPath = getFilePath(selectedDirectory, newDirName);
      const tempFilePath = getFilePath(dirPath, '.temp');
      console.debug(`Creating directory: ${dirPath}`);
      
      // Create the temporary file (this will create the directory)
      const createResponse = await fetch(`${API_BASE_URL}/files/create?path=${encodeURIComponent(tempFilePath)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: '' }),
      });
      
      if (!createResponse.ok) {
        const text = await createResponse.text();
        console.error('API Error Response:', text);
        setErrorMessage(`Error creating directory: Server returned ${createResponse.status}`);
        return;
      }
      
      // Delete the temporary file
      const deleteResponse = await fetch(`${API_BASE_URL}/files/delete?path=${encodeURIComponent(tempFilePath)}`, {
        method: 'DELETE',
      });
      
      if (!deleteResponse.ok) {
        console.error('Error deleting temporary file, but directory was created');
      }
      
      setSuccessMessage(`Successfully created directory ${newDirName}`);
      
      // Reset form
      setNewDirName('');
      setShowCreateDirForm(false);
      
      // Update the directory listing
      onDirectoryChange(selectedDirectory);
    } catch (error) {
      console.error('Error creating directory:', error);
      setErrorMessage('An unexpected error occurred while creating the directory.');
    }
  };

  const getFilePath = (directory: string, fileName: string): string => {
    // Handle path joining correctly
    if (directory.endsWith('/')) {
      return `${directory}${fileName}`;
    } else {
      return `${directory}/${fileName}`;
    }
  };

  const handleCreateInDirectory = (directoryPath: string, type: 'file' | 'directory') => {
    setSelectedDirectory(directoryPath);
    if (type === 'file') {
      setShowCreateFileForm(true);
      setShowCreateDirForm(false);
    } else {
      setShowCreateDirForm(true);
      setShowCreateFileForm(false);
    }
  };

  return (
    <div className="h-full w-full flex flex-col">
      <div className="p-2 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
        <div className="flex items-center">
          <h2 className="text-lg font-semibold">Files</h2>
          <button
            className="ml-2 p-1 text-gray-500 hover:text-gray-700 focus:outline-none"
            onClick={() => setRefreshKey(prev => prev + 1)}
            title="Refresh file tree"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
        <div className="flex items-center">
          <span className="text-xs text-gray-500 mr-2 truncate max-w-[150px]">
            {selectedDirectory === currentDirectory 
              ? 'Working Directory' 
              : `In: ${selectedDirectory.split('/').pop()}`}
          </span>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button 
                className="px-2 py-1 text-sm border rounded hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center"
              >
                <Plus className="h-4 w-4 mr-1" />
                New
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleCreateInDirectory(selectedDirectory, 'file')}>
                <File className="h-4 w-4 mr-2" />
                <span>New File</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleCreateInDirectory(selectedDirectory, 'directory')}>
                <Folder className="h-4 w-4 mr-2" />
                <span>New Directory</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      
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
      
      {/* Create file form */}
      {showCreateFileForm && (
        <div className="p-2 border-b border-gray-200 dark:border-gray-800">
          <form onSubmit={handleCreateFile} className="space-y-2">
            <div>
              <label htmlFor="name" className="block text-sm font-medium">
                File Name
              </label>
              <input
                id="name"
                type="text"
                value={newFileName}
                onChange={(e) => setNewFileName(e.target.value)}
                className="w-full border rounded p-1 text-sm"
                placeholder="example.txt"
              />
            </div>
            <div>
              <label htmlFor="content" className="block text-sm font-medium">
                Content
              </label>
              <textarea
                id="content"
                value={newFileContent}
                onChange={(e) => setNewFileContent(e.target.value)}
                className="w-full border rounded p-1 text-sm h-20"
                placeholder="Enter initial file content (optional)"
              />
            </div>
            <div className="flex justify-end space-x-2">
              <button
                type="button"
                className="px-2 py-1 text-sm border rounded hover:bg-gray-100 dark:hover:bg-gray-800"
                onClick={() => setShowCreateFileForm(false)}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-2 py-1 text-sm border rounded bg-blue-500 text-white hover:bg-blue-600"
              >
                Create
              </button>
            </div>
          </form>
        </div>
      )}
      
      {/* Create directory form */}
      {showCreateDirForm && (
        <div className="p-2 border-b border-gray-200 dark:border-gray-800">
          <form onSubmit={handleCreateDirectory} className="space-y-2">
            <div>
              <label htmlFor="dirName" className="block text-sm font-medium">
                Directory Name
              </label>
              <input
                id="dirName"
                type="text"
                value={newDirName}
                onChange={(e) => setNewDirName(e.target.value)}
                className="w-full border rounded p-1 text-sm"
                placeholder="my-directory"
              />
            </div>
            <div className="flex justify-end space-x-2">
              <button
                type="button"
                className="px-2 py-1 text-sm border rounded hover:bg-gray-100 dark:hover:bg-gray-800"
                onClick={() => setShowCreateDirForm(false)}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-2 py-1 text-sm border rounded bg-blue-500 text-white hover:bg-blue-600"
              >
                Create
              </button>
            </div>
          </form>
        </div>
      )}
      
      {/* File Tree View - takes remaining height */}
      <div className="overflow-auto flex-grow">
        <FileTreeView
          rootDirectory={currentDirectory}
          onFileSelect={onFileSelect}
          currentFile={currentFile}
          onCreateFile={(dirPath) => handleCreateInDirectory(dirPath, 'file')}
          onDirectorySelect={setSelectedDirectory}
          refreshKey={refreshKey}
        />
      </div>
    </div>
  );
};

export default Sidebar;
