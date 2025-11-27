'use client';

import { useVoiceCommands } from '@/hooks/useVoiceCommands';
import { useEffect, useRef, useState } from 'react';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'loading' | 'error';
  content: string;
  timestamp: Date;
}

interface VoiceChatSidebarProps {
  onCommandProcessed?: () => void;
  initialMessages?: any[];
}

export default function VoiceChatSidebar({ onCommandProcessed, initialMessages = [] }: VoiceChatSidebarProps) {
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

  const [messages, setMessages] = useState<Message[]>([]);

  // Load initial messages from chat history
  useEffect(() => {
    if (initialMessages.length > 0) {
      const formattedMessages = initialMessages.map((msg: any) => ({
        id: msg.id,
        type: msg.message_type,
        content: msg.content,
        timestamp: new Date(msg.created_at),
      }));
      setMessages(formattedMessages);
    }
  }, [initialMessages]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const lastTranscriptRef = useRef<string>('');
  const lastResponseRef = useRef<string>('');
  const lastErrorRef = useRef<string>('');
  const onCommandProcessedRef = useRef(onCommandProcessed);
  const isRecordingRef = useRef(isRecording);

  // Update ref when callback changes
  useEffect(() => {
    onCommandProcessedRef.current = onCommandProcessed;
  }, [onCommandProcessed]);

  // Update recording ref when state changes
  useEffect(() => {
    isRecordingRef.current = isRecording;
  }, [isRecording]);

  // Keyboard shortcut: Hold Option/Alt to record
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check if Option/Alt key is pressed (not Cmd/Ctrl to avoid conflicts)
      if (e.altKey && !e.metaKey && !e.ctrlKey && !isRecordingRef.current && !isProcessing) {
        e.preventDefault();
        startRecording();
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      // Check if Option/Alt key is released
      if (e.key === 'Alt' && isRecordingRef.current) {
        e.preventDefault();
        stopRecording();
      }
    };

    // Add event listeners
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    // Cleanup
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isProcessing, startRecording, stopRecording]);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle transcript - only add if it's new
  useEffect(() => {
    if (transcript && !isProcessing && transcript !== lastTranscriptRef.current) {
      lastTranscriptRef.current = transcript;
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'user',
          content: transcript,
          timestamp: new Date(),
        },
      ]);
    }
  }, [transcript, isProcessing]);

  // Handle processing state
  useEffect(() => {
    if (isProcessing) {
      setMessages((prev) => {
        // Remove any existing loading message
        const filtered = prev.filter((m) => m.type !== 'loading');
        return [
          ...filtered,
          {
            id: 'loading',
            type: 'loading',
            content: '',
            timestamp: new Date(),
          },
        ];
      });
    } else {
      // Remove loading message when not processing
      setMessages((prev) => prev.filter((m) => m.type !== 'loading'));
    }
  }, [isProcessing]);

  // Handle response - only add if it's new (handles both success and failure)
  useEffect(() => {
    if (response && response.natural_response && response.natural_response !== lastResponseRef.current) {
      lastResponseRef.current = response.natural_response;
      setMessages((prev) => {
        // Remove loading message
        const filtered = prev.filter((m) => m.type !== 'loading');
        return [
          ...filtered,
          {
            id: Date.now().toString() + '-response',
            type: 'assistant',
            content: response.natural_response,
            timestamp: new Date(),
          },
        ];
      });
      // Only refresh tasks list if the command succeeded
      if (response.success && onCommandProcessedRef.current) {
        onCommandProcessedRef.current();
      }
    }
  }, [response]); // Removed onCommandProcessed from dependencies

  // Handle error - only add if it's new
  useEffect(() => {
    if (error && error !== lastErrorRef.current) {
      lastErrorRef.current = error;
      setMessages((prev) => {
        // Remove loading message
        const filtered = prev.filter((m) => m.type !== 'loading');
        return [
          ...filtered,
          {
            id: Date.now().toString() + '-error',
            type: 'assistant',
            content: '❌ Something went wrong. Please try again.',
            timestamp: new Date(),
          },
        ];
      });
    }
  }, [error]);

  return (
    <div className="flex flex-col h-screen bg-white border-l border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-primary-500 to-purple-600">
        <h2 className="text-xl font-bold text-white flex items-center">
          <svg
            className="w-6 h-6 mr-2"
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
          Voice Assistant
        </h2>
        <p className="text-sm text-white/90 mt-1 flex items-center">
          <span>Hold</span>
          <kbd className="mx-1 px-1.5 py-0.5 text-xs font-semibold bg-white/20 border border-white/30 rounded">
            ⌥ Option
          </kbd>
          <span>to speak</span>
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <p className="text-sm">Click the mic button below to start</p>
            <div className="mt-4 text-xs text-gray-400 space-y-1">
              <p>&quot;Create a task to buy groceries&quot;</p>
              <p>&quot;Show me high priority tasks&quot;</p>
              <p>&quot;Mark first task as completed&quot;</p>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.type === 'loading' ? (
              <div className="bg-gray-100 rounded-lg px-4 py-3 max-w-[80%]">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            ) : (
              <div
                className={`rounded-lg px-4 py-3 max-w-[80%] ${
                  message.type === 'user'
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="text-sm whitespace-pre-wrap break-words">
                  {message.content.split('\n').map((line, i) => {
                    // Handle markdown-style bold text
                    const parts = line.split(/(\*\*.*?\*\*)/g);
                    return (
                      <p key={i} className={i > 0 ? 'mt-1' : ''}>
                        {parts.map((part, j) => {
                          if (part.startsWith('**') && part.endsWith('**')) {
                            return <strong key={j}>{part.slice(2, -2)}</strong>;
                          }
                          return <span key={j}>{part}</span>;
                        })}
                      </p>
                    );
                  })}
                </div>
                <p
                  className={`text-xs mt-2 ${
                    message.type === 'user'
                      ? 'text-white/70'
                      : 'text-gray-500'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Voice Input Area */}
      <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
        {/* Audio Visualizer */}
        {isRecording && (
          <div className="mb-4 bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-center mb-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse delay-75"></div>
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse delay-150"></div>
              </div>
              <span className="ml-3 text-sm text-gray-600 font-medium">
                Listening...
              </span>
            </div>

            {/* Waveform */}
            <div className="flex items-center justify-center h-16 gap-1">
              {[...Array(24)].map((_, i) => {
                const barHeight = Math.max(
                  8,
                  audioLevel * 60 * (0.5 + Math.sin(i * 0.4) * 0.5)
                );
                return (
                  <div
                    key={i}
                    className="bg-gradient-to-t from-primary-400 to-primary-600 rounded-full transition-all duration-75"
                    style={{
                      width: '3px',
                      height: `${barHeight}px`,
                      opacity: 0.6 + audioLevel * 0.4,
                    }}
                  />
                );
              })}
            </div>

            {/* Volume Meter */}
            <div className="mt-2">
              <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-green-400 via-yellow-400 to-red-500 transition-all duration-100"
                  style={{ width: `${audioLevel * 100}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Mic Button */}
        <div className="flex justify-center relative">
          {/* Pulse ring when recording */}
          {isRecording && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-20 h-20 rounded-full bg-red-400 opacity-75 animate-ping"></div>
            </div>
          )}
          
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            className={`
              relative w-16 h-16 rounded-full transition-all duration-300 shadow-lg z-10
              ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 scale-110'
                  : 'bg-primary-500 hover:bg-primary-600'
              }
              ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              disabled:opacity-50
            `}
          >
            {isProcessing ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
              </div>
            ) : (
              <div className="flex items-center justify-center text-white">
                <svg
                  className="w-8 h-8"
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
              </div>
            )}
          </button>
        </div>

        {!isRecording && !isProcessing && (
          <div className="text-center mt-3">
            <p className="text-xs text-gray-600 font-medium">
              Click or hold <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded">Option</kbd> to record
            </p>
          </div>
        )}
        
        {isRecording && (
          <p className="text-xs text-red-600 text-center mt-3 font-medium animate-pulse">
            🔴 Recording... Release Option or click to stop
          </p>
        )}
        
        {isProcessing && (
          <p className="text-xs text-gray-500 text-center mt-3">
            Processing your command...
          </p>
        )}
      </div>
    </div>
  );
}

