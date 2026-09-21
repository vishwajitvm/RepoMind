import React, { useState } from "react";
import { FileCode, Globe, ChevronDown, ChevronRight, Hash } from "lucide-react";
import { Badge } from "../common/Badge";
import { SourceCitation as CitationType } from "../../types";

export interface SourceCitationProps {
  citation: CitationType;
}

export const SourceCitation: React.FC<SourceCitationProps> = ({ citation }) => {
  const [expanded, setExpanded] = useState(false);

  const isLive = citation.source_type === "live_mcp";

  return (
    <div className="flex flex-col border border-border bg-surface-raised/40 hover:border-zinc-600 rounded-lg overflow-hidden transition-all text-xs font-mono">
      <div
        onClick={() => citation.snippet && setExpanded(!expanded)}
        className={`flex items-center justify-between p-2.5 gap-2 select-none ${
          citation.snippet ? "cursor-pointer hover:bg-surface-raised" : ""
        }`}
      >
        <div className="flex items-center gap-2 min-w-0">
          {isLive ? (
            <Globe className="w-4 h-4 text-sky-400 shrink-0" />
          ) : (
            <FileCode className="w-4 h-4 text-emerald-400 shrink-0" />
          )}
          <span className="font-semibold text-gray-200 truncate">
            {citation.path}
          </span>
          {citation.symbol && (
            <span className="hidden sm:inline-flex items-center text-gray-400 text-[11px] gap-0.5">
              <Hash className="w-3 h-3 text-gray-500" />
              {citation.symbol}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[11px] text-gray-400">
            L{citation.start_line}–L{citation.end_line}
          </span>
          <Badge variant={isLive ? "primary" : "neutral"} size="sm">
            {isLive ? "Live MCP" : "Indexed"}
          </Badge>
          {citation.snippet && (
            <span className="text-gray-400">
              {expanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
            </span>
          )}
        </div>
      </div>

      {expanded && citation.snippet && (
        <div className="p-2.5 border-t border-border bg-surface">
          <pre className="text-[11px] text-gray-300 leading-relaxed overflow-x-auto whitespace-pre-wrap">
            {citation.snippet}
          </pre>
        </div>
      )}
    </div>
  );
};
