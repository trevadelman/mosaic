"use client"

import React, { useState, useEffect } from 'react';
import { AgentViewProps } from "@/lib/types/agent-view";
import { useChat } from "@/lib/hooks/use-chat";
import { PromptDialog } from './PromptDialog';
import { AudioFileManager } from './AudioFileManager';

interface AudioFile {
  name: string;
  size: number;
  created: string;
  modified: string;
  format: string;
  url: string;
}

interface AudioData {
  success: boolean;
  format: string;
  voice: string;
  file_info: AudioFile;
}

interface VoiceConfig {
  voice: "alloy" | "echo" | "fable" | "onyx" | "nova" | "shimmer";
  instructions?: string;
}

export const CreatorView: React.FC<AgentViewProps> = ({ agent }) => {
  const { sendMessage, messages, clearChat } = useChat(agent?.id);
  const [audioText, setAudioText] = useState("");
  const [filename, setFilename] = useState("");
  const [voiceConfig, setVoiceConfig] = useState<VoiceConfig>({
    voice: "shimmer"
  });
  const [audioData, setAudioData] = useState<AudioData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Clear state on mount
  useEffect(() => {
    const init = async () => {
      setAudioText("");
      setFilename("");
      setVoiceConfig(prev => ({ ...prev, instructions: "" }));
      setAudioData(null);
      await clearChat();
    };
    init();
  }, []); // Empty dependency array

  // Monitor messages for responses
  useEffect(() => {
    if (!messages?.length) return;
    
    const lastMessage = messages[messages.length - 1];
    if (lastMessage?.role !== 'assistant') return;
    
    try {
      // Try parsing as JSON first (for audio file response)
      const result = typeof lastMessage.content === 'string' 
        ? JSON.parse(lastMessage.content) 
        : lastMessage.content;
      
      if (result.success && result.file_info) {
        setAudioData(result);
        setIsLoading(false);
        return;
      }
    } catch (err) {
      // Not JSON, use as raw text for content/tone responses
      if (typeof lastMessage.content === 'string') {
        const prevMessage = messages[messages.length - 2]?.content;
        
        // Handle voice tone generation
        if (prevMessage?.includes('generate_voice_tone')) {
          setVoiceConfig(prev => ({
            ...prev,
            instructions: lastMessage.content
          }));
          setIsLoading(false);
          return;
        }
        
        // Handle text generation
        if (prevMessage?.includes('generate_content')) {
          setAudioText(lastMessage.content);
          setIsLoading(false);
          return;
        }
      }
    }
  }, [messages]);

  // Handle content generation from prompt
  const handleGenerateAudioText = async (prompt: string) => {
    setIsLoading(true);
    try {
      // Clear conversation first to ensure fresh state
      await clearChat();
      await sendMessage(`generate_content "${prompt}"`);
    } catch (err) {
      console.error('Error generating text:', err);
      setIsLoading(false);
    }
  };

  // Handle voice tone generation from prompt
  const handleGenerateVoiceTone = async (prompt: string) => {
    setIsLoading(true);
    try {
      // Clear conversation first to ensure fresh state
      await clearChat();
      await sendMessage(`generate_voice_tone "${prompt}"`);
    } catch (err) {
      console.error('Error generating tone:', err);
      setIsLoading(false);
    }
  };

  // Handle text-to-speech generation
  const handleGenerateSpeech = async () => {
    if (!audioText.trim()) return;
    setIsLoading(true);

    try {
      // Clear conversation first to ensure fresh state
      await clearChat();
      await sendMessage(`generate_speech "${audioText}" ${JSON.stringify(voiceConfig)} "${filename}"`);
    } catch (err) {
      console.error('Error generating speech:', err);
      setIsLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-2 gap-4 flex-grow">
      {/* Left Panel - Input */}
      <div className="border rounded-lg p-4 space-y-6">
        {/* Filename Input */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-lg font-semibold">Filename</label>
          </div>
          <input
            type="text"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="Enter filename (optional)"
            disabled={isLoading}
          />
        </div>

        {/* Audio Text Section */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-lg font-semibold">Audio Text</label>
            <PromptDialog
              title="Generate Audio Text"
              description="Enter a prompt to generate the text"
              buttonText="Generate Text"
              onGenerate={handleGenerateAudioText}
            />
          </div>
          <textarea
            value={audioText}
            onChange={(e) => setAudioText(e.target.value)}
            className="w-full h-40 p-2 border rounded"
            placeholder="Enter or generate text..."
            disabled={isLoading}
          />
        </div>

        {/* Voice Settings */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-lg font-semibold">Voice Settings</label>
            <PromptDialog
              title="Generate Voice Tone"
              description="Enter a prompt to generate the tone"
              buttonText="Generate Tone"
              onGenerate={handleGenerateVoiceTone}
            />
          </div>
          
          <select
            value={voiceConfig.voice}
            onChange={(e) => setVoiceConfig(prev => ({
              ...prev,
              voice: e.target.value as VoiceConfig["voice"]
            }))}
            className="w-full p-2 border rounded mb-2"
            disabled={isLoading}
          >
            <option value="alloy">Alloy (Versatile, balanced)</option>
            <option value="echo">Echo (Deep, resonant male)</option>
            <option value="fable">Fable (Warm, engaging)</option>
            <option value="onyx">Onyx (Deep, authoritative)</option>
            <option value="nova">Nova (Bright, energetic)</option>
            <option value="shimmer">Shimmer (Clear, professional female)</option>
          </select>

          <textarea
            value={voiceConfig.instructions || ''}
            onChange={(e) => setVoiceConfig(prev => ({
              ...prev,
              instructions: e.target.value
            }))}
            className="w-full h-24 p-2 border rounded"
            placeholder="Enter or generate voice instructions..."
            disabled={isLoading}
          />
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerateSpeech}
          disabled={isLoading || !audioText.trim()}
          className="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 relative"
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Generating...
            </div>
          ) : (
            "Generate Audio"
          )}
        </button>
      </div>

      {/* Right Panel - Audio Player and File Manager */}
      <div className="border rounded-lg p-4 flex flex-col">
        {/* Audio Preview Section */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-4">Audio Preview</h2>
          {audioData ? (
            <div className="space-y-4">
              <audio
                controls
                className="w-full"
                src={`${process.env.NEXT_PUBLIC_API_URL?.replace(/\/api$/, '') || 'http://localhost:8000'}${audioData.file_info.url}`}
              />
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL?.replace(/\/api$/, '') || 'http://localhost:8000'}${audioData.file_info.url}`}
                download
                className="block w-full text-center py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Download Audio
              </a>
            </div>
          ) : (
            <div className="h-32 flex items-center justify-center text-gray-500">
              Generate audio or select a file to preview it here
            </div>
          )}
        </div>

        {/* Audio File Manager Section */}
        <div className="flex-1">
          <h2 className="text-lg font-semibold mb-4">Audio Files</h2>
          <AudioFileManager
            selectedFile={audioData?.file_info}
            onSelectFile={(file) => {
              if (file) {
                setAudioData({
                  success: true,
                  format: file.format,
                  voice: "unknown",
                  file_info: file
                });
              } else {
                setAudioData(null);
              }
            }}
          />
        </div>
      </div>
    </div>
  );
};
