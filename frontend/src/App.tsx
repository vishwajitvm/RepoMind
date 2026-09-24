import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  BrainCircuit,
  Database,
  RefreshCw,
  Activity,
  Layers,
  Sparkles,
  GitBranch,
  X,
  FileCode,
  ShieldAlert,
} from "lucide-react";

import {
  useRepositories,
  useCreateRepository,
  useIndexingStatus,
  useTriggerIndexing,
  useSendChatMessage,
} from "./hooks/useRepoMind";
import { Repository, ChatMessage as ChatMessageType, ExecutionTrace } from "./types";
import { Button } from "./components/common/Button";
import { Input } from "./components/common/Input";
import { Badge } from "./components/common/Badge";
import { Modal } from "./components/common/Modal";
import { Toast } from "./components/common/Toast";
import { RepositorySelector } from "./components/ai/RepositorySelector";
import { ChatInput } from "./components/ai/ChatInput";
import { ChatMessage } from "./components/ai/ChatMessage";
import { ExecutionStep } from "./components/ai/ExecutionStep";

// Zod schema for new repository validation
const addRepoSchema = z.object({
  url: z.string().min(1, "URL is required"),
  name: z.string().optional(),
  default_branch: z.string().default("main"),
});

type AddRepoFormData = z.infer<typeof addRepoSchema>;

export const App: React.FC = () => {
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [activeTrace, setActiveTrace] = useState<ExecutionTrace | null>(null);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: "info" | "success" | "warning" | "error" } | null>(null);
  const [messages, setMessages] = useState<ChatMessageType[]>([]);

  // Server state via TanStack Query
  const { data: repositories = [] } = useRepositories();
  const createRepoMutation = useCreateRepository();
  const triggerIndexMutation = useTriggerIndexing();
  const sendChatMutation = useSendChatMessage();

  // Indexing status for selected repository
  const { data: indexStatus, refetch: refetchStatus } = useIndexingStatus(
    selectedRepo?.id || null
  );

  // Form setup
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AddRepoFormData>({
    resolver: zodResolver(addRepoSchema),
    defaultValues: { default_branch: "main" },
  });

  const onAddRepoSubmit = async (data: AddRepoFormData) => {
    try {
      const newRepo = await createRepoMutation.mutateAsync({
        url: data.url,
        name: data.name || undefined,
        default_branch: data.default_branch || "main",
      });
      setSelectedRepo(newRepo);
      setIsAddModalOpen(false);
      reset();
      setToastMessage({ text: `Registered repository: ${newRepo.name}`, type: "success" });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create repository";
      setToastMessage({ text: msg, type: "error" });
    }
  };

  const handleTriggerIndexing = async (force = false) => {
    if (!selectedRepo) return;
    try {
      await triggerIndexMutation.mutateAsync({ repoId: selectedRepo.id, force });
      setToastMessage({ text: "Indexing job started in background worker.", type: "info" });
      refetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to start indexing";
      setToastMessage({ text: msg, type: "error" });
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!selectedRepo) {
      setToastMessage({ text: "Please select or register a repository first.", type: "warning" });
      return;
    }

    const userMsg: ChatMessageType = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await sendChatMutation.mutateAsync({
        repository_id: selectedRepo.id,
        message: text,
      });

      const asstMsg: ChatMessageType = {
        id: res.message_id,
        role: "assistant",
        content: res.answer,
        sources: res.sources,
        trace: res.trace,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, asstMsg]);

      // If fallback occurred, notify user
      if (res.trace.fallback_occurred) {
        setToastMessage({
          text: `LLM fallback executed: routed to ${res.trace.provider_used} (${res.trace.model_used})`,
          type: "warning",
        });
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Chat request failed";
      setToastMessage({ text: msg, type: "error" });
    }
  };

  const isIndexing =
    indexStatus?.status === "processing" ||
    indexStatus?.status === "pending" ||
    indexStatus?.status === "indexing";

  return (
    <div className="flex flex-col h-screen w-screen bg-background overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-3.5 border-b border-border bg-surface shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-600/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-gray-100 flex items-center gap-2">
              RepoMind
              <Badge variant="primary" size="sm">POC v0.1</Badge>
            </h1>
            <p className="text-[11px] text-gray-400">
              AI Codebase Intelligence • LangGraph • Qdrant • GitHub MCP
            </p>
          </div>
        </div>

        {/* Selected Repo Header Indicator */}
        <div className="flex items-center gap-3">
          {selectedRepo ? (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-raised border border-border rounded-lg text-xs">
              <GitBranch className="w-3.5 h-3.5 text-emerald-400" />
              <span className="font-semibold text-gray-200">{selectedRepo.name}</span>
              <span className="text-gray-500">•</span>
              <span className="text-gray-400 font-mono">{selectedRepo.default_branch}</span>
            </div>
          ) : (
            <span className="text-xs text-gray-500 italic">No repository active</span>
          )}
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left Sidebar: Repositories & Indexing Status */}
        <aside className="w-80 border-r border-border bg-surface/50 p-4 flex flex-col gap-5 overflow-y-auto shrink-0">
          <RepositorySelector
            repositories={repositories}
            selectedRepoId={selectedRepo?.id || null}
            onSelect={(repo) => setSelectedRepo(repo)}
            onAddClick={() => setIsAddModalOpen(true)}
          />

          {/* Indexing Status Box */}
          {selectedRepo && (
            <div className="flex flex-col gap-3 p-3.5 border border-border bg-surface rounded-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-gray-200">
                  <Database className="w-4 h-4 text-emerald-400" />
                  <span>Indexing Engine</span>
                </div>
                <Badge
                  variant={
                    isIndexing
                      ? "warning"
                      : indexStatus?.status === "completed" || selectedRepo.status === "indexed"
                      ? "success"
                      : "neutral"
                  }
                  size="sm"
                >
                  {isIndexing ? "Indexing..." : indexStatus?.status || selectedRepo.status}
                </Badge>
              </div>

              {/* Progress Metrics */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="bg-surface-raised p-2 rounded border border-border/60">
                  <span className="text-[10px] text-gray-500 block uppercase">Files Indexed</span>
                  <span className="font-bold text-gray-200">
                    {indexStatus?.indexed_files || 0} / {indexStatus?.total_files || 0}
                  </span>
                </div>
                <div className="bg-surface-raised p-2 rounded border border-border/60">
                  <span className="text-[10px] text-gray-500 block uppercase">Qdrant Chunks</span>
                  <span className="font-bold text-gray-200">
                    {indexStatus?.total_chunks || 0}
                  </span>
                </div>
              </div>

              {indexStatus?.failed_files !== undefined && indexStatus.failed_files > 0 && (
                <div className="text-[11px] text-amber-400 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
                  <span>{indexStatus.failed_files} file(s) failed or skipped safely</span>
                </div>
              )}

              <Button
                variant="primary"
                size="sm"
                fullWidth
                disabled={isIndexing}
                loading={isIndexing}
                icon={<RefreshCw className="w-3.5 h-3.5" />}
                onClick={() => handleTriggerIndexing(true)}
              >
                {isIndexing ? "Indexing Active..." : "Re-Index Codebase"}
              </Button>
            </div>
          )}

          {/* Quick Info */}
          <div className="mt-auto pt-3 border-t border-border text-[11px] text-gray-500 flex flex-col gap-1.5">
            <div className="flex items-center gap-1.5 text-gray-400 font-semibold">
              <Layers className="w-3.5 h-3.5 text-emerald-400" />
              <span>Multi-Provider Fallback</span>
            </div>
            <p>Gemini → Groq → NVIDIA → OpenRouter → Ollama (Local)</p>
          </div>
        </aside>

        {/* Center Panel: AI Chat */}
        <main className="flex-1 flex flex-col overflow-hidden bg-background">
          {/* Messages list */}
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto gap-4">
                <div className="w-12 h-12 rounded-2xl bg-emerald-600/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-inner">
                  <Sparkles className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-gray-200">
                    Welcome to RepoMind
                  </h3>
                  <p className="text-xs text-gray-400 mt-1">
                    Ask natural-language questions about this repository. RepoMind retrieves AST-parsed code chunks from Qdrant, calls GitHub MCP for live sources, and synthesizes answers with citations.
                  </p>
                </div>

                <div className="flex flex-col gap-2 w-full text-left">
                  <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">
                    Suggested Questions
                  </span>
                  {[
                    "What is the high-level architecture of this codebase?",
                    "How does the LLMRouter handle provider timeouts and fallback?",
                    "Explain the code chunking strategy and file filtering rules.",
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(q)}
                      className="p-2.5 rounded-lg border border-border bg-surface hover:bg-surface-raised text-xs text-gray-300 text-left transition-colors flex items-center gap-2"
                    >
                      <FileCode className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{q}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((m) => (
                <ChatMessage
                  key={m.id}
                  message={m}
                  onViewTrace={(trace) => setActiveTrace(trace)}
                />
              ))
            )}
          </div>

          {/* Chat Input Bar */}
          <div className="p-4 border-t border-border bg-surface/40 shrink-0">
            <ChatInput
              onSend={handleSendMessage}
              loading={sendChatMutation.isPending}
              disabled={!selectedRepo}
              placeholder={
                selectedRepo
                  ? `Ask RepoMind about ${selectedRepo.name}...`
                  : "Please select a repository on the left first"
              }
            />
          </div>
        </main>

        {/* Right Drawer: Execution Trace Inspector */}
        {activeTrace && (
          <aside className="w-96 border-l border-border bg-surface p-4 flex flex-col gap-4 overflow-y-auto shrink-0 animate-in slide-in-from-right duration-200">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2 text-sm font-bold text-gray-100">
                <Activity className="w-4 h-4 text-emerald-400" />
                <span>Execution Trace</span>
              </div>
              <button
                onClick={() => setActiveTrace(null)}
                className="text-gray-400 hover:text-gray-200 p-1 rounded-lg hover:bg-surface-raised transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Overview */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="bg-surface-raised p-2.5 rounded border border-border">
                <span className="text-[10px] text-gray-500 uppercase block">Provider</span>
                <span className="font-bold text-emerald-400 capitalize">
                  {activeTrace.provider_used}
                </span>
              </div>
              <div className="bg-surface-raised p-2.5 rounded border border-border">
                <span className="text-[10px] text-gray-500 uppercase block">Model</span>
                <span className="font-bold text-gray-200 truncate block">
                  {activeTrace.model_used}
                </span>
              </div>
              <div className="bg-surface-raised p-2.5 rounded border border-border">
                <span className="text-[10px] text-gray-500 uppercase block">Latency</span>
                <span className="font-bold text-gray-200">
                  {activeTrace.latency_ms}ms
                </span>
              </div>
              <div className="bg-surface-raised p-2.5 rounded border border-border">
                <span className="text-[10px] text-gray-500 uppercase block">Chunks Found</span>
                <span className="font-bold text-gray-200">
                  {activeTrace.retrieval_chunks_count}
                </span>
              </div>
            </div>

            {/* Fallback Chain */}
            {activeTrace.fallback_chain && activeTrace.fallback_chain.length > 0 && (
              <div className="flex flex-col gap-2">
                <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                  Provider Fallback Chain
                </span>
                <div className="flex flex-col gap-1.5">
                  {activeTrace.fallback_chain.map((fb, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2 rounded bg-surface-raised text-xs font-mono border border-border/70"
                    >
                      <span className="text-gray-200 capitalize">{fb.provider}</span>
                      <div className="flex items-center gap-1.5">
                        <span className="text-gray-500 text-[10px]">{fb.latency_ms}ms</span>
                        <Badge variant={fb.status === "success" ? "success" : "danger"} size="sm">
                          {fb.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* LangGraph Pipeline Steps */}
            <div className="flex flex-col gap-2">
              <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                LangGraph Pipeline Steps
              </span>
              <div className="flex flex-col gap-2">
                {activeTrace.steps.map((st, idx) => (
                  <ExecutionStep key={st.name + idx} step={st} stepNumber={idx + 1} />
                ))}
              </div>
            </div>
          </aside>
        )}
      </div>

      {/* Add Repository Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Register Repository for Indexing"
      >
        <form onSubmit={handleSubmit(onAddRepoSubmit)} className="flex flex-col gap-4">
          <Input
            label="GitHub Repository URL or Local Path"
            placeholder="https://github.com/owner/repository"
            error={errors.url?.message}
            {...register("url")}
          />
          <Input
            label="Display Name (Optional)"
            placeholder="owner/repo"
            error={errors.name?.message}
            {...register("name")}
          />
          <Input
            label="Default Branch"
            placeholder="main"
            error={errors.default_branch?.message}
            {...register("default_branch")}
          />
          <div className="flex justify-end gap-2 pt-3 border-t border-border">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => setIsAddModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              loading={createRepoMutation.isPending}
            >
              Register &amp; Prepare
            </Button>
          </div>
        </form>
      </Modal>

      {/* Toast Notification Container */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 max-w-sm">
          <Toast
            type={toastMessage.type}
            message={toastMessage.text}
            onClose={() => setToastMessage(null)}
          />
        </div>
      )}
    </div>
  );
};
