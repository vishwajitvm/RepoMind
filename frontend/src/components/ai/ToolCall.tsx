import React from "react";
import { Terminal, CheckCircle2, AlertCircle, Clock } from "lucide-react";
import { Spinner } from "../common/Spinner";
import { Badge } from "../common/Badge";
import { clsx } from "clsx";

export interface ToolCallProps {
  toolName: string;
  server?: string;
  status: "idle" | "running" | "success" | "error";
  latencyMs?: number;
  args?: Record<string, unknown>;
  output?: Record<string, unknown> | string;
  error?: string;
  expanded?: boolean;
}

export const ToolCall: React.FC<ToolCallProps> = ({
  toolName,
  server,
  status,
  latencyMs,
  args,
  output,
  error,
  expanded = false,
}) => {
  const [isExpanded, setIsExpanded] = React.useState(expanded);
  const statusIcons = {
    idle: <Clock className="w-4 h-4 text-gray-400" />,
    running: <Spinner size="sm" color="#10b981" />,
    success: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
    error: <AlertCircle className="w-4 h-4 text-red-400" />,
  };

  const statusBadges = {
    idle: <Badge variant="neutral" size="sm">Idle</Badge>,
    running: <Badge variant="primary" size="sm">Running</Badge>,
    success: <Badge variant="success" size="sm">Success</Badge>,
    error: <Badge variant="danger" size="sm">Failed</Badge>,
  };

  return (
    <div className="flex flex-col border border-border bg-surface rounded-lg p-3 text-xs font-mono gap-2 transition-all">
      <div className="flex items-center justify-between cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          {server && (
            <span className="text-[10px] text-sky-400 bg-sky-950/40 px-1.5 py-0.5 rounded border border-sky-800/40">
              {server}
            </span>
          )}
          <span className="font-semibold text-gray-200">{toolName}</span>
        </div>
        <div className="flex items-center gap-2">
          {latencyMs !== undefined && latencyMs > 0 && (
            <span className="text-gray-400 text-[11px]">{latencyMs}ms</span>
          )}
          {statusBadges[status]}
          <span className="shrink-0">{statusIcons[status]}</span>
        </div>
      </div>

      {(isExpanded || status === "running") && args && Object.keys(args).length > 0 && (
        <div className="bg-surface-raised rounded p-2 text-gray-300 overflow-x-auto">
          <div className="text-[10px] text-gray-500 font-semibold mb-1 uppercase tracking-wide">
            Arguments
          </div>
          <pre className="text-[11px] leading-relaxed">
            {JSON.stringify(args, null, 2)}
          </pre>
        </div>
      )}

      {error && (
        <div className="rounded p-2 bg-red-950/30 text-red-300 border border-red-900/40 overflow-x-auto">
          <div className="text-[10px] text-red-400 font-semibold mb-1 uppercase tracking-wide">
            Error
          </div>
          <pre className="text-[11px] leading-relaxed">{error}</pre>
        </div>
      )}

      {(isExpanded || status !== "idle") && output && (
        <div
          className={clsx(
            "rounded p-2 overflow-x-auto",
            status === "error"
              ? "bg-red-950/30 text-red-300 border border-red-900/40"
              : "bg-surface-raised text-gray-300"
          )}
        >
          <div className="text-[10px] text-gray-500 font-semibold mb-1 uppercase tracking-wide">
            Result
          </div>
          <pre className="text-[11px] leading-relaxed">
            {typeof output === "string"
              ? output
              : JSON.stringify(output, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
