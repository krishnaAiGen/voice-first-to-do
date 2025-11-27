'use client';

import { useState, useEffect, useCallback } from 'react';
import { Task } from '@/types/task';
import { taskApi } from '@/lib/api';

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedTasks = await taskApi.getTasks();
      setTasks(fetchedTasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const refreshTasks = useCallback(() => {
    fetchTasks();
  }, [fetchTasks]);

  const updateTaskLocally = (updatedTask: Task) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) => (task.id === updatedTask.id ? updatedTask : task))
    );
  };

  const deleteTaskLocally = (taskId: string) => {
    setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
  };

  const addTaskLocally = (newTask: Task) => {
    setTasks((prevTasks) => [newTask, ...prevTasks]);
  };

  return {
    tasks,
    loading,
    error,
    refreshTasks,
    updateTaskLocally,
    deleteTaskLocally,
    addTaskLocally,
  };
}

