import { Repository, IndexStatus, ChatResponse, ExecutionTrace } from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

export async function fetchRepositories(): Promise<Repository[]> {
  const res = await fetch(`${API_BASE}/repositories`);
  if (!res.ok) {
    throw new Error(`Failed to fetch repositories: ${res.statusText}`);
  }
  return res.json();
}

export async function createRepository(payload: {
  url: string;
  name?: string;
  default_branch?: string;
}): Promise<Repository> {
  const res = await fetch(`${API_BASE}/repositories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new Error(`Failed to create repository: ${res.statusText}`);
  }
  return res.json();
}

export async function triggerIndexing(
  repoId: string,
  forceReindex = false
): Promise<IndexStatus> {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/index`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ force_reindex: forceReindex })
  });
  if (!res.ok) {
    throw new Error(`Failed to trigger indexing: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchIndexingStatus(repoId: string): Promise<IndexStatus> {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/status`);
  if (!res.ok) {
    throw new Error(`Failed to fetch status: ${res.statusText}`);
  }
  return res.json();
}

export async function sendChatMessage(payload: {
  repository_id: string;
  message: string;
  conversation_id?: string;
}): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new Error(`Chat request failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchExecutionTrace(
  executionId: string
): Promise<ExecutionTrace> {
  const res = await fetch(`${API_BASE}/executions/${executionId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch execution trace: ${res.statusText}`);
  }
  return res.json();
}
