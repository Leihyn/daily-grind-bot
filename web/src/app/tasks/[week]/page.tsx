"use client";

import { useEffect, useState, use } from "react";
import { TaskItem } from "@/components/task-item";
import { SaveButton } from "@/components/save-button";
import { TasksData } from "@/lib/types";

export default function WeekEditorPage({
  params,
}: {
  params: Promise<{ week: string }>;
}) {
  const { week } = use(params);
  const weekNum = parseInt(week, 10);

  const [tasks, setTasks] = useState<string[]>([]);
  const [sha, setSha] = useState("");
  const [allData, setAllData] = useState<TasksData | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/tasks")
      .then((r) => r.json())
      .then((data) => {
        const { _sha, ...rest } = data;
        setSha(_sha);
        setAllData(rest as TasksData);
        const weekTasks =
          rest.weekly_tasks[String(weekNum)] ?? rest.maintenance_tasks ?? [];
        setTasks([...weekTasks]);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load tasks");
        setLoading(false);
      });
  }, [weekNum]);

  function updateTask(index: number, text: string) {
    setTasks((prev) => prev.map((t, i) => (i === index ? text : t)));
    setSaved(false);
  }

  function removeTask(index: number) {
    setTasks((prev) => prev.filter((_, i) => i !== index));
    setSaved(false);
  }

  function addTask() {
    setTasks((prev) => [...prev, ""]);
    setSaved(false);
  }

  async function save() {
    if (!allData) return;
    setSaving(true);
    setError("");

    const updatedData: TasksData & { _sha: string } = {
      ...allData,
      weekly_tasks: {
        ...allData.weekly_tasks,
        [String(weekNum)]: tasks.filter((t) => t.trim() !== ""),
      },
      _sha: sha,
    };

    try {
      const res = await fetch("/api/tasks", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedData),
      });

      if (!res.ok) {
        const body = await res.json();
        throw new Error(body.error || "Save failed");
      }

      setSaved(true);

      // Refetch to get new SHA
      const fresh = await fetch("/api/tasks").then((r) => r.json());
      setSha(fresh._sha);
      const { _sha: _, ...rest } = fresh;
      setAllData(rest as TasksData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-zinc-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">
            Week {weekNum}
          </h1>
          <p className="text-sm text-zinc-400">{tasks.length} tasks</p>
        </div>
        <div className="flex items-center gap-3">
          {saved && (
            <span className="text-sm text-green-400">Saved</span>
          )}
          {error && (
            <span className="text-sm text-red-400">{error}</span>
          )}
          <SaveButton onClick={save} saving={saving} />
        </div>
      </div>

      <div className="flex flex-col gap-2 mb-4">
        {tasks.map((task, i) => (
          <TaskItem
            key={i}
            task={task}
            completed={false}
            editable
            onTextChange={(text) => updateTask(i, text)}
            onDelete={() => removeTask(i)}
          />
        ))}
      </div>

      <button
        onClick={addTask}
        className="w-full rounded-lg border border-dashed border-zinc-700 py-2 text-sm text-zinc-400 hover:border-zinc-500 hover:text-zinc-300 transition-colors"
      >
        + Add task
      </button>
    </div>
  );
}
