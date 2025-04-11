import React, { useState, useEffect } from 'react';
import { Editor } from '@monaco-editor/react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';
import { xetoApi } from '@/lib/api';

interface XetoEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  jsonPath: string;
  manufacturer: string;
  model: string;
}

export function XetoEditorModal({
  isOpen,
  onClose,
  jsonPath,
  manufacturer,
  model,
}: XetoEditorModalProps) {
  // Editor states
  const [libContent, setLibContent] = useState('');
  const [specsContent, setSpecsContent] = useState('');
  const [activeTab, setActiveTab] = useState('lib');
  
  // Operation states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [compileOutput, setCompileOutput] = useState<string | null>(null);
  const [compileSuccess, setCompileSuccess] = useState(false);

  // Load initial content
  useEffect(() => {
    if (isOpen && jsonPath) {
      loadXetoContent();
    }
  }, [isOpen, jsonPath]);

  // Load Xeto content from JSON
  const loadXetoContent = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await xetoApi.convertToXeto({
        json_path: jsonPath,
        manufacturer,
        model,
      });

      if (response.data.success) {
        setLibContent(response.data.lib_content || '');
        setSpecsContent(response.data.specs_content || '');
      } else {
        setError(response.data.error || 'Failed to convert JSON to Xeto');
      }
    } catch (err) {
      setError('Error loading Xeto content: ' + (err as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  // Attempt to compile Xeto library
  const handleCompile = async () => {
    setIsLoading(true);
    setError(null);
    setCompileOutput(null);
    setCompileSuccess(false);

    try {
      const response = await xetoApi.compileXeto({
        lib_content: libContent,
        specs_content: specsContent,
        manufacturer,
        model,
      });

      // Always show the output if it exists
      if (response.data.output) {
        setCompileOutput(response.data.output);
      }

      if (response.data.success) {
        setCompileSuccess(true);
      } else {
        setError(response.data.error || 'Compilation failed');
        setCompileSuccess(false);
      }
    } catch (err) {
      setError('Error compiling Xeto: ' + (err as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  // Save Xeto files
  const handleSave = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await xetoApi.saveXeto({
        lib_content: libContent,
        specs_content: specsContent,
        manufacturer,
        model,
      });

      if (response.data.success) {
        onClose();
      } else {
        setError(response.data.error || 'Failed to save Xeto files');
      }
    } catch (err) {
      setError('Error saving Xeto files: ' + (err as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-[90vw] h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Xeto Library Editor</DialogTitle>
        </DialogHeader>

        <div className="flex-1 flex flex-col overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList>
              <TabsTrigger value="lib">lib.xeto</TabsTrigger>
              <TabsTrigger value="specs">specs.xeto</TabsTrigger>
              {compileOutput && (
                <TabsTrigger value="output">Compilation Output</TabsTrigger>
              )}
            </TabsList>

            <TabsContent value="lib" className="flex-1 min-h-0 data-[state=active]:flex">
              <Editor
                height="100%"
                className="w-full"
                defaultLanguage="plaintext"
                value={libContent}
                onChange={(value) => setLibContent(value || '')}
                options={{
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  theme: 'vs-dark',
                  readOnly: false,
                }}
              />
            </TabsContent>

            <TabsContent value="specs" className="flex-1 min-h-0 data-[state=active]:flex">
              <Editor
                height="100%"
                className="w-full"
                defaultLanguage="plaintext"
                value={specsContent}
                onChange={(value) => setSpecsContent(value || '')}
                options={{
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  theme: 'vs-dark',
                  readOnly: false,
                }}
              />
            </TabsContent>

            {compileOutput && (
              <TabsContent value="output" className="flex-1 min-h-0 data-[state=active]:flex">
                <div className={`w-full overflow-auto p-4 rounded-md ${compileSuccess ? 'bg-green-900/20' : 'bg-red-900/20'}`}>
                  <div className="mb-2 font-semibold">
                    {compileSuccess ? 'Compilation Successful' : 'Compilation Failed'}
                  </div>
                  <pre className="whitespace-pre-wrap font-mono text-sm">{compileOutput}</pre>
                </div>
              </TabsContent>
            )}
          </Tabs>

          {error && (
            <Alert variant="destructive" className="mt-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex justify-end gap-2 mt-4">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            
            <Button
              variant="secondary"
              onClick={handleCompile}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Compiling...
                </>
              ) : (
                'Attempt Compile'
              )}
            </Button>
            
            <Button
              onClick={handleSave}
              disabled={isLoading || !compileSuccess}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save to Storage'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
