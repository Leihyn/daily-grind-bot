import Link from "next/link";
import { WeekSummary } from "@/lib/types";

interface WeekCardProps {
  summary: WeekSummary;
  isCurrent?: boolean;
}

export function WeekCard({ summary, isCurrent = false }: WeekCardProps) {
  const progress = summary.total > 0 ? summary.done / summary.total : 0;
  const percentage = Math.round(progress * 100);

  return (
    <Link
      href={`/tasks/${summary.week}`}
      className={`block rounded-xl border p-4 transition-colors hover:border-zinc-600 ${
        isCurrent
          ? "border-green-700 bg-green-950/20"
          : "border-zinc-800 bg-zinc-900"
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-white">
          Week {summary.week}
        </span>
        {isCurrent && (
          <span className="text-xs text-green-400 font-medium">Current</span>
        )}
      </div>

      <div className="w-full bg-zinc-800 rounded-full h-2 mb-2">
        <div
          className="bg-green-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>

      <span className="text-xs text-zinc-400">
        {summary.done}/{summary.total} tasks ({percentage}%)
      </span>
    </Link>
  );
}
