"use client";

interface TaskItemProps {
  task: string;
  completed: boolean;
  editable?: boolean;
  onTextChange?: (text: string) => void;
  onDelete?: () => void;
}

export function TaskItem({
  task,
  completed,
  editable = false,
  onTextChange,
  onDelete,
}: TaskItemProps) {
  if (editable) {
    return (
      <div className="flex items-start gap-3 rounded-lg border border-zinc-800 bg-zinc-900 p-3 group">
        <input
          type="text"
          value={task}
          onChange={(e) => onTextChange?.(e.target.value)}
          className="flex-1 bg-transparent text-sm text-white outline-none placeholder-zinc-500"
          placeholder="Task description..."
        />
        <button
          onClick={onDelete}
          className="text-zinc-600 hover:text-red-400 text-sm opacity-0 group-hover:opacity-100 transition-opacity"
          title="Remove task"
        >
          x
        </button>
      </div>
    );
  }

  return (
    <div
      className={`flex items-start gap-3 rounded-lg border p-3 ${
        completed
          ? "border-green-900/50 bg-green-950/30"
          : "border-zinc-800 bg-zinc-900"
      }`}
    >
      <div
        className={`mt-0.5 h-4 w-4 shrink-0 rounded-full border-2 ${
          completed
            ? "border-green-500 bg-green-500"
            : "border-zinc-600"
        }`}
      />
      <span
        className={`text-sm ${
          completed ? "text-zinc-400 line-through" : "text-zinc-200"
        }`}
      >
        {task}
      </span>
    </div>
  );
}
