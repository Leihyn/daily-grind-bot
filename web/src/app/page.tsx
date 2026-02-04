import { ProgressRing } from "@/components/progress-ring";
import { TaskList } from "@/components/task-list";
import { TasksData, StateData } from "@/lib/types";
import {
  getCurrentWeek,
  getWeekSummary,
  getOverallProgress,
  getTotalWeeks,
} from "@/lib/utils";

async function fetchData(): Promise<{
  tasks: TasksData;
  state: StateData;
} | null> {
  const base = process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000";
  try {
    const [tasksRes, stateRes] = await Promise.all([
      fetch(`${base}/api/tasks`, { cache: "no-store" }),
      fetch(`${base}/api/state`, { cache: "no-store" }),
    ]);
    if (!tasksRes.ok || !stateRes.ok) return null;
    const tasks = await tasksRes.json();
    const state = await stateRes.json();
    return { tasks, state };
  } catch {
    return null;
  }
}

export default async function Dashboard() {
  const data = await fetchData();

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <h2 className="text-xl font-bold text-zinc-300">
          Could not load data
        </h2>
        <p className="text-sm text-zinc-500">
          Check your GitHub API credentials in environment variables.
        </p>
      </div>
    );
  }

  const { tasks, state } = data;
  const currentWeek = getCurrentWeek(state.start_date);
  const weekSummary = getWeekSummary(tasks, state, currentWeek);
  const overall = getOverallProgress(tasks, state);
  const totalWeeks = getTotalWeeks(tasks);

  const monthNumber = Math.ceil(currentWeek / 4);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Dashboard</h1>
        <p className="text-sm text-zinc-400">
          Week {currentWeek} of {totalWeeks} &middot; Month {monthNumber}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 flex flex-col items-center gap-3">
          <h3 className="text-sm font-medium text-zinc-400">This Week</h3>
          <ProgressRing done={weekSummary.done} total={weekSummary.total} />
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 flex flex-col items-center gap-3">
          <h3 className="text-sm font-medium text-zinc-400">
            Overall Roadmap
          </h3>
          <ProgressRing done={overall.done} total={overall.total} />
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-white mb-4">
          Week {currentWeek} Tasks
        </h2>
        <TaskList
          tasks={weekSummary.tasks}
          completedIndices={weekSummary.completedIndices}
        />
      </div>
    </div>
  );
}
