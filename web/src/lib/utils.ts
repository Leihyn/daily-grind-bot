import { TasksData, StateData, WeekSummary } from "./types";

export function getCurrentWeek(startDate: string): number {
  const start = new Date(startDate);
  const now = new Date();
  const diffMs = now.getTime() - start.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  return Math.max(1, Math.floor(diffDays / 7) + 1);
}

export function getTasksForWeek(
  tasks: TasksData,
  week: number
): string[] {
  return tasks.weekly_tasks[String(week)] ?? tasks.maintenance_tasks;
}

export function getWeekSummary(
  tasks: TasksData,
  state: StateData,
  week: number
): WeekSummary {
  const weekTasks = getTasksForWeek(tasks, week);
  const completedIndices = state.completed[String(week)] ?? [];
  return {
    week,
    tasks: weekTasks,
    completedIndices,
    total: weekTasks.length,
    done: completedIndices.length,
  };
}

export function getTotalWeeks(tasks: TasksData): number {
  const keys = Object.keys(tasks.weekly_tasks).map(Number);
  return Math.max(...keys);
}

export function getOverallProgress(
  tasks: TasksData,
  state: StateData
): { done: number; total: number } {
  const totalWeeks = getTotalWeeks(tasks);
  let done = 0;
  let total = 0;
  for (let w = 1; w <= totalWeeks; w++) {
    const weekTasks = getTasksForWeek(tasks, w);
    total += weekTasks.length;
    done += (state.completed[String(w)] ?? []).length;
  }
  return { done, total };
}
