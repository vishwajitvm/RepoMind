import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchRepositories,
  createRepository,
  triggerIndexing,
  fetchIndexingStatus,
  sendChatMessage,
  fetchExecutionTrace
} from "../api/client";

export function useRepositories() {
  return useQuery({
    queryKey: ["repositories"],
    queryFn: fetchRepositories
  });
}

export function useCreateRepository() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createRepository,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repositories"] });
    }
  });
}

export function useIndexingStatus(repoId: string | null) {
  return useQuery({
    queryKey: ["indexingStatus", repoId],
    queryFn: () => (repoId ? fetchIndexingStatus(repoId) : null),
    enabled: Boolean(repoId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "processing" || status === "pending" || status === "indexing"
        ? 2000
        : false;
    }
  });
}

export function useTriggerIndexing() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ repoId, force }: { repoId: string; force?: boolean }) =>
      triggerIndexing(repoId, force),
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: ["indexingStatus", vars.repoId] });
      queryClient.invalidateQueries({ queryKey: ["repositories"] });
    }
  });
}

export function useSendChatMessage() {
  return useMutation({
    mutationFn: sendChatMessage
  });
}

export function useExecutionTrace(executionId: string | null) {
  return useQuery({
    queryKey: ["executionTrace", executionId],
    queryFn: () => (executionId ? fetchExecutionTrace(executionId) : null),
    enabled: Boolean(executionId)
  });
}
