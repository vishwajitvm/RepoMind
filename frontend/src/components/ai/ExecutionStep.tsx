import React, { useState } from "react";
import { CheckCircle2, Clock, AlertCircle, ChevronDown, ChevronRight } from "lucide-react";
import { Spinner } from "../common/Spinner";
import { Badge } from "../common/Badge";
import { ExecutionStepItem } from "../../types";

export interface ExecutionStepProps {
  step: ExecutionStepItem;
  stepNumber?: number;
}

export const ExecutionStep: React.FC<ExecutionStepProps> = ({
  step,
  stepNumber,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const statusIcons = {
    pending: <Clock className="w-4 h-4 text-gray-400" />,
    running: <Spinner size="sm" color="#10b981" />,
    success: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
    error: <AlertCircle className="w-4 h-4 text-red-400" />,
    skipped: <Clock className="w-4 h-4 text-gray-500" />,
  };

  const hasDetails = step.details && Object.keys(step.details).length > 0;

  return (
    <div className="flex flex-col border border-border bg-surface rounded-lg overflow-hidden transition-all text-sm">
      <div
        onClick={() => hasDetails && setIsOpen(!isOpen)}
        className={`flex items-center justify-between p-3 select-none ${
          hasDetails ? "cursor-pointer hover:bg-surface-raised/50" : ""
        }`}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <span className="shrink-0">{statusIcons[step.status]}</span>
          {stepNumber !== undefined && (
            <span className="text-xs font-mono text-gray-500 font-semibold">
              0{stepNumber}.
            </span>
          )}
          <span className="font-medium text-gray-200 truncate capitalize">
            {step.name.replace(/_/g, " ")}
          </span>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {step.latency_ms > 0 && (
            <span className="text-xs text-gray-400 font-mono">
              {step.latency_ms}ms
            </span>
          )}
          <Badge
            variant={
              step.status === "success"
                ? "success"
                : step.status === "error"
                ? "danger"
                : step.status === "running"
                ? "primary"
                : "neutral"
            }
            size="sm"
          >
            {step.status}
          </Badge>
          {hasDetails && (
            <span className="text-gray-400">
              {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </span>
          )}
        </div>
      </div>

      {isOpen && hasDetails && (
        <div className="px-3 pb-3 pt-1 border-t border-border/60 bg-surface-raised/30">
          <pre className="text-xs font-mono text-gray-300 bg-surface p-2 rounded border border-border/80 overflow-x-auto">
            {JSON.stringify(step.details, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
