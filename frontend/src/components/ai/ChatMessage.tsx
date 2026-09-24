import React from "react";
import { Bot, User, Activity } from "lucide-react";
import { SourceCitation } from "./SourceCitation";
import { Button } from "../common/Button";
import { ChatMessage as ChatMessageType, ExecutionTrace } from "../../types";

export interface ChatMessageProps {
  message: ChatMessageType;
  onViewTrace?: (trace: ExecutionTrace) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onViewTrace,
}) => {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex gap-3.5 p-4 rounded-xl transition-all ${
        isUser
          ? "bg-surface-raised/60 border border-border/80 self-end max-w-2xl ml-auto"
          : "bg-surface border border-border self-start w-full"
      }`}
    >
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 shadow-sm ${
          isUser
            ? "bg-zinc-700 text-gray-200"
            : "bg-emerald-600/20 text-emerald-400 border border-emerald-500/30"
        }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      <div className="flex flex-col gap-2.5 flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-gray-300">
            {isUser ? "You" : "RepoMind"}
          </span>
          <span className="text-[10px] text-gray-500 font-mono">
            {new Date(message.created_at).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        </div>

        <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="flex flex-col gap-1.5 mt-2 pt-2 border-t border-border">
            <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              Sources Cited ({message.sources.length})
            </span>
            <div className="flex flex-col gap-1.5">
              {message.sources.map((src, i) => (
                <SourceCitation key={`${src.path}-${src.start_line}-${i}`} citation={src} />
              ))}
            </div>
          </div>
        )}

        {!isUser && message.trace && (
          <div className="flex items-center justify-between mt-1 pt-2 border-t border-border/60">
            <div className="flex items-center gap-2 text-xs text-gray-400 font-mono">
              <span>Provider: <strong className="text-gray-300">{message.trace.provider_used}</strong></span>
              <span>•</span>
              <span>Model: <strong className="text-gray-300">{message.trace.model_used}</strong></span>
              <span>•</span>
              <span>{message.trace.latency_ms}ms</span>
            </div>
            {onViewTrace && (
              <Button
                variant="ghost"
                size="sm"
                icon={<Activity className="w-3.5 h-3.5 text-emerald-400" />}
                onClick={() => onViewTrace(message.trace!)}
                className="text-xs text-emerald-400 hover:text-emerald-300 p-1.5"
              >
                Inspect Trace
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
