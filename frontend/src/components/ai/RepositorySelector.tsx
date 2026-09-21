import React from "react";
import { GitFork, Plus, Check } from "lucide-react";
import { Button } from "../common/Button";
import { Badge } from "../common/Badge";
import { Repository } from "../../types";

export interface RepositorySelectorProps {
  repositories: Repository[];
  selectedRepoId: string | null;
  onSelect: (repo: Repository) => void;
  onAddClick: () => void;
  loading?: boolean;
  disabled?: boolean;
  error?: string;
}

export const RepositorySelector: React.FC<RepositorySelectorProps> = ({
  repositories,
  selectedRepoId,
  onSelect,
  onAddClick,
  loading = false,
  disabled = false,
  error,
}) => {
  return (
    <div className="flex flex-col gap-3 w-full">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">
          Repositories
        </h3>
        <Button
          variant="outline"
          size="sm"
          disabled={disabled || loading}
          icon={<Plus className="w-3.5 h-3.5" />}
          onClick={onAddClick}
        >
          Add Repo
        </Button>
      </div>

      {error && (
        <div className="p-2.5 rounded-lg border border-red-500/30 bg-red-950/20 text-xs text-red-300">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center p-6 border border-dashed border-border rounded-lg text-xs text-gray-400">
          Loading repositories...
        </div>
      ) : (
        <div className="flex flex-col gap-1.5 max-h-60 overflow-y-auto pr-1">
          {repositories.length === 0 ? (
            <div className="text-center p-4 border border-dashed border-border rounded-lg text-xs text-gray-400">
              No repositories registered yet. Click &quot;Add Repo&quot; to begin.
            </div>
          ) : (
          repositories.map((repo) => {
            const isSelected = repo.id === selectedRepoId;
            return (
              <div
                key={repo.id}
                onClick={() => onSelect(repo)}
                className={`flex items-center justify-between p-2.5 rounded-lg border cursor-pointer transition-all select-none text-xs ${
                  isSelected
                    ? "bg-emerald-950/30 border-emerald-500/50 text-emerald-300 shadow-sm"
                    : "bg-surface border-border hover:bg-surface-raised text-gray-300"
                }`}
              >
                <div className="flex items-center gap-2 truncate min-w-0">
                  <GitFork className="w-4 h-4 shrink-0 text-gray-400" />
                  <span className="font-medium truncate">{repo.name}</span>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Badge
                    variant={
                      repo.status === "indexed"
                        ? "success"
                        : repo.status === "indexing"
                        ? "warning"
                        : repo.status === "failed"
                        ? "danger"
                        : "neutral"
                    }
                    size="sm"
                  >
                    {repo.status}
                  </Badge>
                  {isSelected && <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                </div>
              </div>
            );
          })
        )}
        </div>
      )}
    </div>
  );
};
