'use client';

import { useVoiceCommands } from '@/hooks/useVoiceCommands';
import { useEffect } from 'react';

interface VoiceRecorderProps {
  onCommandProcessed?: () => void;
}

export default function VoiceRecorder({ onCommandProcessed }: VoiceRecorderProps) {
  const {
    isRecording,
    isProcessing,
    transcript,
    response,
    error,
    audioLevel,
    startRecording,
    stopRecording,
  } = useVoiceCommands();

  useEffect(() => {
    if (response && response.success && onCommandProcessed) {
      onCommandProcessed();
    }
  }, [response, onCommandProcessed]);

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-2xl shadow-xl p-8">
        {/* Voice Button */}
        <div className="flex justify-center mb-6">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            className={`
              relative w-32 h-32 rounded-full transition-all duration-300 shadow-lg
              ${isRecording 
                ? 'bg-red-500 hover:bg-red-600 scale-110' 
                : 'bg-primary-500 hover:bg-primary-600'
              }
              ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              disabled:opacity-50
            `}
          >
            {isProcessing ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-white">
                <svg
                  className="w-12 h-12 mb-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
                <span className="text-sm font-medium">
                  {isRecording ? 'Stop' : 'Speak'}
                </span>
              </div>
            )}
          </button>
        </div>

        {/* Audio Visualizer */}
        {isRecording && (
          <div className="mb-6">
            <div className="flex items-center justify-center mb-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse delay-75"></div>
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse delay-150"></div>
              </div>
              <span className="ml-3 text-sm text-gray-600">Recording...</span>
            </div>
            
            {/* Audio Waveform Visualization */}
            <div className="flex items-center justify-center h-24 gap-1 px-4">
              {[...Array(32)].map((_, i) => {
                // Create a wave effect based on audio level and position
                const barHeight = Math.max(
                  10,
                  audioLevel * 100 * (0.5 + Math.sin(i * 0.4) * 0.5)
                );
                return (
                  <div
                    key={i}
                    className="bg-gradient-to-t from-primary-400 to-primary-600 rounded-full transition-all duration-75"
                    style={{
                      width: '4px',
                      height: `${barHeight}px`,
                      opacity: 0.6 + audioLevel * 0.4,
                    }}
                  />
                );
              })}
            </div>
            
            {/* Audio Level Indicator */}
            <div className="mt-3 px-8">
              <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-green-400 via-yellow-400 to-red-500 transition-all duration-100"
                  style={{ width: `${audioLevel * 100}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 text-center mt-1">
                Volume: {Math.round(audioLevel * 100)}%
              </p>
            </div>
          </div>
        )}

        {/* Processing Indicator */}
        {isProcessing && (
          <div className="text-center mb-4">
            <p className="text-sm text-gray-600">Processing your command...</p>
          </div>
        )}

        {/* Transcript */}
        {transcript && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500 mb-1">You said:</p>
            <p className="text-gray-900 font-medium">{transcript}</p>
          </div>
        )}

        {/* Response */}
        {response && response.success && (
          <div className="mb-4 p-4 bg-green-50 rounded-lg border border-green-200">
            <p className="text-sm text-green-600 mb-1">Success!</p>
            <p className="text-gray-900">{response.natural_response}</p>
            {response.latency_ms && (
              <p className="text-xs text-gray-500 mt-2">
                Processed in {response.latency_ms.toFixed(0)}ms
              </p>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 rounded-lg border border-red-200">
            <p className="text-sm text-red-600 mb-1">Error</p>
            <p className="text-gray-900">{error}</p>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Click the microphone and say commands like:
          </p>
          <div className="mt-2 space-y-1 text-xs text-gray-500">
            <p>&quot;Create a task to buy groceries tomorrow&quot;</p>
            <p>&quot;Show me all high priority tasks&quot;</p>
            <p>&quot;Mark the first task as completed&quot;</p>
            <p>&quot;Delete the third task&quot;</p>
          </div>
        </div>
      </div>
    </div>
  );
}

