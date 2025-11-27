'use client';

import { Task } from '@/types/task';
import { format } from 'date-fns';

interface TaskCardProps {
  task: Task;
}

const priorityColors = {
  0: 'bg-gray-100 text-gray-700',
  1: 'bg-blue-100 text-blue-700',
  2: 'bg-yellow-100 text-yellow-700',
  3: 'bg-red-100 text-red-700',
};

const priorityLabels = {
  0: 'None',
  1: 'Low',
  2: 'Medium',
  3: 'High',
};

const statusColors = {
  pending: 'bg-gray-100 text-gray-700',
  in_progress: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
};

const statusLabels = {
  pending: 'Pending',
  in_progress: 'In Progress',
  completed: 'Completed',
};

export default function TaskCard({ task }: TaskCardProps) {
  const priorityColor = priorityColors[task.priority as keyof typeof priorityColors];
  const priorityLabel = priorityLabels[task.priority as keyof typeof priorityLabels];
  const statusColor = statusColors[task.status];
  const statusLabel = statusLabels[task.status];

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow duration-200">
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-lg font-semibold text-gray-900 flex-1">
          {task.title}
        </h3>
        <div className="flex gap-2 ml-2">
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${priorityColor}`}
          >
            {priorityLabel}
          </span>
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor}`}
          >
            {statusLabel}
          </span>
        </div>
      </div>

      {task.description && (
        <p className="text-gray-600 text-sm mb-3">{task.description}</p>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-3">
          {task.category && (
            <span className="flex items-center">
              <svg
                className="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                />
              </svg>
              {task.category}
            </span>
          )}
          {task.scheduled_time && (
            <span className="flex items-center">
              <svg
                className="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              {format(new Date(task.scheduled_time), 'MMM d, yyyy')}
            </span>
          )}
        </div>
        <span>
          Created {format(new Date(task.created_at), 'MMM d')}
        </span>
      </div>
    </div>
  );
}

