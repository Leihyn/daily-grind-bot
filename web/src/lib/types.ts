export interface TasksData {
  weekly_tasks: Record<string, string[]>;
  maintenance_tasks: string[];
}

export interface StateData {
  start_date: string;
  completed: Record<string, number[]>;
  seen_issues: string[];
  notify_index: number;
  last_update_id: number;
}

export interface WeekSummary {
  week: number;
  tasks: string[];
  completedIndices: number[];
  total: number;
  done: number;
}
