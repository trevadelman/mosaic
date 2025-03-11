"use client"

import React, { useState, useEffect } from 'react';
import { Folder, File, Plus, Trash, ChevronRight, ChevronDown } from 'lucide-react';
import ConfirmationDialog from './ConfirmationDialog';
import { cn } from "@/lib/utils";

interface FileTreeViewProps {
  rootDirectory: string;
  onFileSelect: (filePath: string) => void;
  currentFile: string | null;
  onCreateFile?: (directoryPath: string) => void;
  onDirectorySelect?: (directoryPath: string) => void;
  refreshKey?: number; // A key that changes to trigger a refresh
}

interface TreeNode {
  name: string;
  path: string;
  isDirectory: boolean;
  children: TreeNode[];
  isLoaded: boolean;
}

const FileTreeView: React.FC<FileTreeViewProps> = ({
  rootDirectory,
  onFileSelect,
  currentFile,
  onCreateFile,
  onDirectorySelect,
  refreshKey,
}) => {
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState<boolean>(false);
  const [itemToDelete, setItemToDelete] = useState<TreeNode | null>(null);

  // Get the API base URL from environment variables
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

  // Load the root directory on component mount or when refreshKey changes
  useEffect(() => {
    loadDirectory(rootDirectory, true);
  }, [rootDirectory, refreshKey]);

  // Function to load a directory and its contents
  const loadDirectory = async (directoryPath: string, isRoot: boolean = false) => {
    try {
      setIsLoading(true);
      console.debug(`Fetching directory contents for: ${directoryPath}`);
      
      const response = await fetch(`${API_BASE_URL}/files/list?path=${encodeURIComponent(directoryPath)}`);
      
      if (!response.ok) {
        const text = await response.text();
        console.error('API Error Response:', text);
        setErrorMessage(`Error loading directory: Server returned ${response.status}`);
        return;
      }
      
      const data = await response.json();
      console.debug('API Response data:', data);
      
      if (data.error) {
        console.error(data.error);
        setErrorMessage(`Error loading directory: ${data.error}`);
        return;
      }
      
      // Create tree nodes for directories and files
      const directories = data.directories.map((name: string) => ({
        name,
        path: getFilePath(directoryPath, name),
        isDirectory: true,
        children: [],
        isLoaded: false,
      }));
      
      const files = data.files.map((name: string) => ({
        name,
        path: getFilePath(directoryPath, name),
        isDirectory: false,
        children: [],
        isLoaded: true,
      }));
      
      // Sort directories and files alphabetically
      const sortedDirectories = directories.sort((a: TreeNode, b: TreeNode) => a.name.localeCompare(b.name));
      const sortedFiles = files.sort((a: TreeNode, b: TreeNode) => a.name.localeCompare(b.name));
      
      // Combine directories and files
      const children = [...sortedDirectories, ...sortedFiles];
      
      if (isRoot) {
        // For the root directory, we don't want to show the "code-editor-working-dir" node itself
        // Instead, we'll show its children as the top-level items
        
        // Create a virtual root node that won't be displayed
        const rootNode: TreeNode = {
          name: getDirectoryName(directoryPath),
          path: directoryPath,
          isDirectory: true,
          children,
          isLoaded: true,
        };
        
        setTree(rootNode);
        
        // Expand the root node
        setExpandedItems(new Set([directoryPath]));
      } else {
        // Update the existing tree
        setTree((prevTree) => {
          if (!prevTree) return null;
          
          // Create a new tree with the updated node
          return updateTreeNode(prevTree, directoryPath, (node) => ({
            ...node,
            children,
            isLoaded: true,
          }));
        });
      }
    } catch (error) {
      console.error('Error loading directory contents:', error);
      setErrorMessage('An unexpected error occurred while loading the directory contents.');
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to get a file path
  const getFilePath = (directory: string, fileName: string): string => {
    // Handle path joining correctly
    if (directory.endsWith('/')) {
      return `${directory}${fileName}`;
    } else {
      return `${directory}/${fileName}`;
    }
  };

  // Helper function to get the directory name from a path
  const getDirectoryName = (path: string): string => {
    // Get the last part of the path
    const parts = path.split('/');
    return parts[parts.length - 1] || path;
  };

  // Helper function to update a node in the tree
  const updateTreeNode = (
    node: TreeNode,
    path: string,
    updateFn: (node: TreeNode) => TreeNode
  ): TreeNode => {
    if (node.path === path) {
      // This is the node to update
      return updateFn(node);
    } else if (node.isDirectory && path.startsWith(node.path)) {
      // The node to update is in this directory's children
      return {
        ...node,
        children: node.children.map((child) => updateTreeNode(child, path, updateFn)),
      };
    } else {
      // The node to update is not in this branch
      return node;
    }
  };

  // Handle toggle of a directory node
  const handleToggleDirectory = (node: TreeNode) => {
    // Toggle the expanded state
    setExpandedItems((prevExpandedItems) => {
      const newExpandedItems = new Set(prevExpandedItems);
      if (newExpandedItems.has(node.path)) {
        newExpandedItems.delete(node.path);
      } else {
        newExpandedItems.add(node.path);
        
        // Load the directory contents if not already loaded
        if (!node.isLoaded) {
          loadDirectory(node.path);
        }
      }
      return newExpandedItems;
    });
    
    // Notify parent component that a directory was selected
    if (onDirectorySelect) {
      onDirectorySelect(node.path);
    }
  };

  // Handle click on a file node
  const handleFileClick = (node: TreeNode) => {
    onFileSelect(node.path);
    
    // Also update the selected directory to the parent directory of the file
    if (onDirectorySelect) {
      // Get the parent directory path
      const parentPath = node.path.substring(0, node.path.lastIndexOf('/'));
      // If the parent path is empty, use the root directory
      const dirPath = parentPath || rootDirectory;
      onDirectorySelect(dirPath);
    }
  };

  // Handle delete button click
  const handleDeleteClick = (node: TreeNode, e: React.MouseEvent) => {
    e.stopPropagation();
    setItemToDelete(node);
    setIsDeleteDialogOpen(true);
  };

  // Handle delete confirmation
  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;

    try {
      if (itemToDelete.isDirectory) {
        await deleteDirectory(itemToDelete.path);
      } else {
        await deleteFile(itemToDelete.path);
      }

      // Close the dialog
      setIsDeleteDialogOpen(false);
      setItemToDelete(null);

      // Refresh the parent directory
      const parentPath = itemToDelete.path.substring(0, itemToDelete.path.lastIndexOf('/'));
      loadDirectory(parentPath.length > 0 ? parentPath : rootDirectory);

      // If the deleted item was the current file, clear the selection
      if (currentFile === itemToDelete.path) {
        onFileSelect('');
      }
    } catch (error) {
      console.error('Error deleting item:', error);
      setErrorMessage('An unexpected error occurred while deleting the item.');
    }
  };

  // Handle delete cancellation
  const handleDeleteCancel = () => {
    setIsDeleteDialogOpen(false);
    setItemToDelete(null);
  };

  // Delete a file
  const deleteFile = async (filePath: string) => {
    const response = await fetch(`${API_BASE_URL}/files/delete?path=${encodeURIComponent(filePath)}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const text = await response.text();
      console.error('API Error Response:', text);
      throw new Error(`Error deleting file: Server returned ${response.status}`);
    }

    return response.json();
  };

  // Delete a directory using the dedicated endpoint
  const deleteDirectory = async (dirPath: string) => {
    const response = await fetch(`${API_BASE_URL}/files/delete-directory?path=${encodeURIComponent(dirPath)}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const text = await response.text();
      console.error('API Error Response:', text);
      throw new Error(`Error deleting directory: Server returned ${response.status}`);
    }

    return response.json();
  };

  // Render a tree node
  const renderTreeNode = (node: TreeNode, level: number = 0) => {
    const isExpanded = expandedItems.has(node.path);
    const paddingLeft = `${level * 16}px`;
    
    return (
      <div key={node.path} className="select-none">
        <div
          className={cn(
            "flex items-center py-1 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer group",
            currentFile === node.path && "bg-blue-100 dark:bg-blue-900"
          )}
          style={{ paddingLeft }}
          onClick={() => {
            if (node.isDirectory) {
              handleToggleDirectory(node);
            } else {
              handleFileClick(node);
            }
          }}
        >
          {node.isDirectory ? (
            <>
              <span className="mr-1">
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </span>
              <Folder className="h-4 w-4 mr-1 text-blue-500" />
            </>
          ) : (
            <>
              <span className="mr-1 w-4"></span>
              <File className="h-4 w-4 mr-1 text-gray-500" />
            </>
          )}
          <span className="truncate">{node.name}</span>
          
          <div className="ml-auto flex items-center">
            {/* Delete button */}
            <button
              className="mr-1 opacity-0 group-hover:opacity-100 hover:opacity-100 focus:opacity-100 h-6 w-6 p-0 text-gray-500 hover:text-red-500"
              onClick={(e) => handleDeleteClick(node, e)}
              title={`Delete ${node.isDirectory ? 'directory' : 'file'}`}
            >
              <Trash className="h-4 w-4" />
            </button>
            
            {/* Create button (only for directories) */}
            {node.isDirectory && onCreateFile && (
              <button
                className="mr-1 opacity-0 group-hover:opacity-100 hover:opacity-100 focus:opacity-100 h-6 w-6 p-0 text-gray-500 hover:text-gray-700"
                onClick={(e) => {
                  e.stopPropagation();
                  onCreateFile(node.path);
                }}
                title="Create new item"
              >
                <Plus className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
        
        {node.isDirectory && isExpanded && (
          <div>
            {node.children.map((child) => renderTreeNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  if (isLoading && !tree) {
    return (
      <div className="flex justify-center items-center h-full">
        <p>Loading...</p>
      </div>
    );
  }

  if (errorMessage && !tree) {
    return (
      <div className="p-4 text-red-500">
        <p>{errorMessage}</p>
      </div>
    );
  }

  if (!tree) {
    return (
      <div className="flex justify-center items-center h-full">
        <p className="text-gray-500">No files or directories</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto p-2">
      {/* Render the children of the root node directly instead of the root node itself */}
      {tree && tree.children.map((child) => renderTreeNode(child, 0))}
      
      {/* Confirmation Dialog for Delete */}
      <ConfirmationDialog
        isOpen={isDeleteDialogOpen}
        title={`Delete ${itemToDelete?.isDirectory ? 'Directory' : 'File'}`}
        message={`Are you sure you want to delete ${itemToDelete?.isDirectory ? 'directory' : 'file'} "${itemToDelete?.name}"? ${
          itemToDelete?.isDirectory ? 'This will delete all files and subdirectories inside it.' : ''
        }`}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </div>
  );
};

export default FileTreeView;
