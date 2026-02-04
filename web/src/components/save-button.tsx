"use client";

interface SaveButtonProps {
  onClick: () => void;
  saving: boolean;
  disabled?: boolean;
}

export function SaveButton({ onClick, saving, disabled = false }: SaveButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={saving || disabled}
      className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {saving ? "Saving..." : "Save to GitHub"}
    </button>
  );
}
