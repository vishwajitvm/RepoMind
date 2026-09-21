import React from "react";
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from "lucide-react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface ToastProps {
  type?: "info" | "success" | "warning" | "error";
  message: string;
  onClose?: () => void;
  className?: string;
}

export const Toast: React.FC<ToastProps> = ({
  type = "info",
  message,
  onClose,
  className,
}) => {
  const icons = {
    info: <Info className="w-4 h-4 text-sky-400" />,
    success: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
    warning: <AlertTriangle className="w-4 h-4 text-amber-400" />,
    error: <AlertCircle className="w-4 h-4 text-red-400" />,
  };

  const borderStyles = {
    info: "border-sky-500/30 bg-sky-950/40 text-sky-200",
    success: "border-emerald-500/30 bg-emerald-950/40 text-emerald-200",
    warning: "border-amber-500/30 bg-amber-950/40 text-amber-200",
    error: "border-red-500/30 bg-red-950/40 text-red-200",
  };

  return (
    <div
      role="alert"
      className={twMerge(
        clsx(
          "flex items-center justify-between gap-3 px-4 py-3 rounded-lg border text-sm shadow-lg backdrop-blur-md transition-all animate-in fade-in slide-in-from-top-2",
          borderStyles[type],
          className
        )
      )}
    >
      <div className="flex items-center gap-2.5">
        <span className="shrink-0">{icons[type]}</span>
        <span className="font-medium">{message}</span>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-200 p-0.5 rounded transition-colors"
          aria-label="Dismiss toast"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
