'use client';

import { useState, useEffect } from 'react';
import VoiceChatSidebar from '@/components/VoiceChatSidebar';
import TaskList from '@/components/TaskList';
import LoginForm from '@/components/Auth/LoginForm';
import { useTasks } from '@/hooks/useTasks';
import { chatApi } from '@/lib/api';

interface User {
  id: string;
  email: string;
  display_name: string | null;
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [sidebarWidth, setSidebarWidth] = useState(384); // 384px = w-96 (24rem)
  const [isResizing, setIsResizing] = useState(false);

  const { tasks, loading: tasksLoading, error, refreshTasks } = useTasks(isAuthenticated);

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
    const storedWidth = localStorage.getItem('sidebar_width');

    if (storedWidth) {
      setSidebarWidth(parseInt(storedWidth));
    }

    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
        setIsAuthenticated(true);
        loadChatHistory();
      } catch (e) {
        // Invalid stored data
        localStorage.clear();
      }
    }
    setLoading(false);
  }, []);

  const loadChatHistory = async () => {
    try {
      const history = await chatApi.getHistory(50, 0);
      setChatHistory(history.messages || []);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const handleLoginSuccess = (accessToken: string, refreshToken: string, userData: User) => {
    // Store tokens and user data
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    localStorage.setItem('user', JSON.stringify(userData));

    // Update state
    setUser(userData);
    setIsAuthenticated(true);

    // Load chat history
    loadChatHistory();
  };

  const handleLogout = () => {
    // Clear localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');

    // Clear state
    setUser(null);
    setIsAuthenticated(false);
    setChatHistory([]);
  };

  // Handle sidebar resizing
  const startResizing = () => {
    setIsResizing(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;

      const newWidth = window.innerWidth - e.clientX;
      
      // Constrain width between 300px and 800px
      if (newWidth >= 300 && newWidth <= 800) {
        setSidebarWidth(newWidth);
        localStorage.setItem('sidebar_width', newWidth.toString());
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.body.classList.remove('resizing');
    };

    if (isResizing) {
      document.body.classList.add('resizing');
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.body.classList.remove('resizing');
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show login form if not authenticated
  if (!isAuthenticated) {
    return <LoginForm onSuccess={handleLoginSuccess} />;
  }

  // Show main app if authenticated
  return (
    <main className="min-h-screen flex bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <header className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-2">
                Voice-First To-Do
              </h1>
              <p className="text-gray-600 text-lg">
                Welcome back, <strong>{user?.display_name || user?.email}</strong>! 👋
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Logout
            </button>
          </header>

          {/* Task List */}
          <div className="max-w-6xl">
            <TaskList tasks={tasks} loading={tasksLoading} error={error} />
          </div>

          {/* Footer */}
          <footer className="mt-16 text-sm text-gray-500">
            <p>
              Built with FastAPI, Gemini 2.5 Flash, Deepgram, and Next.js
            </p>
          </footer>
        </div>
      </div>

      {/* Resize Handle */}
      <div
        className={`relative w-1 bg-gray-200 hover:bg-primary-400 cursor-col-resize transition-all duration-150 group ${
          isResizing ? 'bg-primary-500 w-1.5' : ''
        }`}
        onMouseDown={startResizing}
        style={{ cursor: 'col-resize' }}
      >
        {/* Grip dots indicator */}
        <div className="absolute inset-y-0 left-1/2 transform -translate-x-1/2 flex flex-col items-center justify-center space-y-1 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
        </div>
        {/* Invisible wider hit area for easier grabbing */}
        <div className="absolute inset-y-0 -left-2 -right-2 w-5" />
      </div>

      {/* Voice Chat Sidebar */}
      <aside 
        className="flex-shrink-0 shadow-2xl"
        style={{ width: `${sidebarWidth}px` }}
      >
        <VoiceChatSidebar 
          onCommandProcessed={() => {
            // Refresh tasks in background (non-blocking)
            setTimeout(() => refreshTasks(), 0);
            // Removed loadChatHistory() - messages already in VoiceChatSidebar state
          }}
          initialMessages={chatHistory}
        />
      </aside>
    </main>
  );
}

