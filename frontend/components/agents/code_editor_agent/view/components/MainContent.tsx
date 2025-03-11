import React from 'react';
import CodeEditor from './CodeEditor';

interface MainContentProps {
  content: string;
  onChange: (content: string) => void;
  onSave: () => void;
  onExplain?: () => void;
  onImprove?: () => void;
  onGenerate?: () => void;
  isLoading: boolean;
  currentFile: string | null;
}

const MainContent: React.FC<MainContentProps> = ({
  content,
  onChange,
  onSave,
  onExplain,
  onImprove,
  onGenerate,
  isLoading,
  currentFile,
}) => {
  return (
    <div className="h-full w-full">
      <CodeEditor
        content={content}
        onChange={onChange}
        onSave={onSave}
        onExplain={onExplain}
        onImprove={onImprove}
        onGenerate={onGenerate}
        isLoading={isLoading}
        currentFile={currentFile}
      />
    </div>
  );
};

export default MainContent;
