import React, { useState } from 'react';
import { AgentViewProps } from "@/lib/types/agent-view";

interface Message {
  type: 'user' | 'ai';
  text: string;
  audioUrl?: string;
}

export const ConversationView: React.FC<AgentViewProps> = ({ tools }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  const processAudio = async (audioBlob: Blob, stream: MediaStream) => {
    setIsProcessing(true);
    try {
      // Convert blob to data URL
      const reader = new FileReader();
      const audioDataUrl = await new Promise<string>((resolve, reject) => {
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = () => reject(new Error('Failed to read audio file'));
        reader.readAsDataURL(audioBlob);
      });
      
      // Transcribe audio
      const transcriptionResult = await tools.transcribe_audio(
        audioDataUrl,
        JSON.stringify({
          response_format: "json",
          timestamp_granularities: ["word"],
          prompt: "This is a conversation with an AI podcaster."
        })
      );
      
      const data = typeof transcriptionResult === 'string' 
        ? JSON.parse(transcriptionResult) 
        : transcriptionResult;

      if (data.success) {
        // Add user message
        setMessages(prev => [...prev, {
          type: 'user',
          text: data.text
        }]);

        // Generate AI response
        const responseResult = await tools.generate_content(
          `Respond to this message in a natural, conversational podcast style: "${data.text}"`
        );
        
        // Handle both string and object responses
        let responseText: string;
        if (typeof responseResult === 'string') {
          try {
            // Try to parse as JSON first
            const responseData = JSON.parse(responseResult);
            if (responseData.error) {
              throw new Error(responseData.error);
            }
            responseText = responseData.text;
          } catch (err) {
            // If not JSON, use the string directly
            responseText = responseResult;
          }
        } else {
          // Handle object response
          if (responseResult.error) {
            throw new Error(responseResult.error);
          }
          responseText = responseResult.text || responseResult;
        }

        // Generate speech for AI response
        const speechResult = await tools.generate_speech(
          responseText,
          JSON.stringify({
            voice: "shimmer",
            model: "tts-1",
            output_format: "mp3",
            speed: 1.0
          })
        );

        const speechData = typeof speechResult === 'string'
          ? JSON.parse(speechResult)
          : speechResult;

        if (speechData.success) {
          // Add message and clear chat
          setMessages(prev => [...prev, {
            type: 'ai',
            text: responseText,
            audioUrl: `${process.env.NEXT_PUBLIC_API_URL?.replace(/\/api$/, '') || 'http://localhost:8000'}${speechData.file_info.url}`
          }]);
          
          // Clear chat after successful audio generation
          await tools.clearChat();
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error processing audio:', err);
    } finally {
      setIsProcessing(false);
      stream.getTracks().forEach(track => track.stop());
    }
  };

  const handleRecording = async () => {
    if (isRecording) {
      // Stop recording
      mediaRecorder?.stop();
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        
        // Store chunks in a local array
        const chunks: Blob[] = [];
        
        recorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            chunks.push(e.data);
          }
        };
        
        recorder.onstop = async () => {
          const audioBlob = new Blob(chunks, { type: 'audio/wav' });
          await processAudio(audioBlob, stream);
        };
        
        setMediaRecorder(recorder);
        recorder.start();
        setIsRecording(true);
      } catch (err) {
        setError('Could not access microphone. Please check permissions.');
        console.error('Error accessing microphone:', err);
      }
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Messages Area */}
      <div className="flex-grow overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800'
              }`}
            >
              {message.text}
              {message.audioUrl && (
                <audio
                  controls
                  className="mt-2 w-full"
                  src={message.audioUrl}
                />
              )}
            </div>
          </div>
        ))}
        {messages.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            Start a conversation by recording your message
          </div>
        )}
      </div>

      {/* Recording Controls */}
      <div className="p-4 border-t">
        <div className="flex justify-center items-center gap-4">
          {/* Error Display */}
          {error && (
            <div className="mb-4 text-red-500 text-sm text-center">
              {error}
              <button
                onClick={() => setError(null)}
                className="ml-2 text-red-700 hover:text-red-800"
              >
                ✕
              </button>
            </div>
          )}
          
          {/* Recording Controls */}
          <button
            onClick={handleRecording}
            disabled={isProcessing}
            className={`p-4 rounded-full ${
              isRecording
                ? 'bg-red-600 animate-pulse'
                : 'bg-blue-500 hover:bg-blue-600'
            } text-white disabled:opacity-50 transition-colors`}
          >
            {isRecording ? '⬤' : '🎤'}
          </button>
        </div>
        <p className="text-center text-sm text-gray-500 mt-2">
          {isRecording
            ? 'Recording... Click again to stop'
            : isProcessing
            ? 'Processing...'
            : 'Click microphone to start recording'}
        </p>
      </div>
    </div>
  );
};
