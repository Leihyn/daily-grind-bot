import { TaskItem } from "./task-item";

interface TaskListProps {
  tasks: string[];
  completedIndices: number[];
}

export function TaskList({ tasks, completedIndices }: TaskListProps) {
  return (
    <div className="flex flex-col gap-2">
      {tasks.map((task, i) => (
        <TaskItem
          key={i}
          task={task}
          completed={completedIndices.includes(i)}
        />
      ))}
    </div>
  );
}
