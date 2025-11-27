'use client';

import VoiceChatSidebar from '@/components/VoiceChatSidebar';
import TaskList from '@/components/TaskList';
import { useTasks } from '@/hooks/useTasks';

export default function Home() {
  const { tasks, loading, error, refreshTasks } = useTasks();

  return (
    <main className="min-h-screen flex bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <header className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-2">
              Voice-First To-Do
            </h1>
            <p className="text-gray-600 text-lg">
              Manage your tasks with natural voice commands
            </p>
          </header>

          {/* Task List */}
          <div className="max-w-6xl">
            <TaskList tasks={tasks} loading={loading} error={error} />
          </div>

          {/* Footer */}
          <footer className="mt-16 text-sm text-gray-500">
            <p>
              Built with FastAPI, Gemini 2.5 Flash, Deepgram, and Next.js
            </p>
          </footer>
        </div>
      </div>

      {/* Voice Chat Sidebar */}
      <aside className="w-96 flex-shrink-0 shadow-2xl">
        <VoiceChatSidebar onCommandProcessed={refreshTasks} />
      </aside>
    </main>
  );
}

