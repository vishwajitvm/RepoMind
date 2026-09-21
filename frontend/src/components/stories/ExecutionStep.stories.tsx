import type { Meta, StoryObj } from "@storybook/react";
import { ExecutionStep } from "../ai/ExecutionStep";

const meta: Meta<typeof ExecutionStep> = {
  title: "AI/ExecutionStep",
  component: ExecutionStep,
};

export default meta;
type Story = StoryObj<typeof ExecutionStep>;

export const QdrantRetrieval: Story = {
  args: {
    stepNumber: 1,
    step: {
      name: "qdrant_retrieval",
      status: "success",
      latency_ms: 18,
      details: {
        chunks_found: 5,
        embedding_provider: "local",
        files: ["backend/app/services/indexer.py", "backend/app/services/code_parser.py"],
      },
    },
  },
};

export const McpDecisionStep: Story = {
  args: {
    stepNumber: 2,
    step: {
      name: "mcp_decision",
      status: "success",
      latency_ms: 2,
      details: {
        needs_mcp: true,
        reason: "User query asked for recent pull requests and live HEAD commit.",
      },
    },
  },
};

export const LLMRoutingWithFallback: Story = {
  args: {
    stepNumber: 3,
    step: {
      name: "llm_routing_generation",
      status: "success",
      latency_ms: 420,
      details: {
        provider_used: "groq",
        model_used: "llama-3.3-70b-versatile",
        fallback_occurred: true,
        fallback_chain: [
          { provider: "gemini", status: "failed", error: "Connection timeout after 25s" },
          { provider: "groq", status: "success", latency_ms: 420 },
        ],
      },
    },
  },
};
