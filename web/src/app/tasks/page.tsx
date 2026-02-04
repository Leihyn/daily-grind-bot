import { WeekCard } from "@/components/week-card";
import { TasksData, StateData } from "@/lib/types";
import { getCurrentWeek, getWeekSummary, getTotalWeeks } from "@/lib/utils";

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

export default async function TasksPage() {
  const data = await fetchData();

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <h2 className="text-xl font-bold text-zinc-300">
          Could not load data
        </h2>
        <p className="text-sm text-zinc-500">
          Check your GitHub API credentials.
        </p>
      </div>
    );
  }

  const { tasks, state } = data;
  const currentWeek = getCurrentWeek(state.start_date);
  const totalWeeks = getTotalWeeks(tasks);
  const weeks = Array.from({ length: totalWeeks }, (_, i) => i + 1);

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">All Weeks</h1>
        <p className="text-sm text-zinc-400">
          Click a week to edit its tasks
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {weeks.map((week) => (
          <WeekCard
            key={week}
            summary={getWeekSummary(tasks, state, week)}
            isCurrent={week === currentWeek}
          />
        ))}
      </div>
    </div>
  );
}
