export interface Repository {
  id: string;
  name: string;
  url: string;
  default_branch: string;
  status: "unindexed" | "indexing" | "indexed" | "failed";
  last_indexed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface IndexStatus {
  repository_id: string;
  status: "pending" | "processing" | "completed" | "failed" | "unindexed" | "indexing" | "indexed";
  total_files: number;
  indexed_files: number;
  failed_files: number;
  total_chunks: number;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
}

export interface SourceCitation {
  path: string;
  symbol?: string | null;
  start_line: number;
  end_line: number;
  source_type: "indexed" | "live_mcp";
  language?: string | null;
  snippet?: string | null;
}

export interface ExecutionStepItem {
  name: string;
  status: "pending" | "running" | "success" | "error" | "skipped";
  latency_ms: number;
  details: Record<string, unknown>;
}

export interface FallbackEvent {
  provider: string;
  model: string;
  status: "failed" | "success";
  error?: string | null;
  latency_ms: number;
}

export interface ExecutionTrace {
  id: string;
  query: string;
  provider_used: string;
  model_used: string;
  fallback_occurred: boolean;
  fallback_chain: FallbackEvent[];
  mcp_invoked: boolean;
  mcp_tools_called: string[];
  retrieval_chunks_count: number;
  latency_ms: number;
  steps: ExecutionStepItem[];
  created_at: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
  trace?: ExecutionTrace;
  created_at: string;
}

export interface ChatResponse {
  message_id: string;
  conversation_id: string;
  answer: string;
  sources: SourceCitation[];
  execution_id: string;
  trace: ExecutionTrace;
}
