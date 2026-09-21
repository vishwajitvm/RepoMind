import type { Meta, StoryObj } from "@storybook/react";
import { ChatMessage } from "../ai/ChatMessage";

const meta: Meta<typeof ChatMessage> = {
  title: "AI/ChatMessage",
  component: ChatMessage,
};

export default meta;
type Story = StoryObj<typeof ChatMessage>;

export const UserQuestion: Story = {
  args: {
    message: {
      id: "msg-1",
      role: "user",
      content: "Where is the LLMRouter implemented and how does provider fallback work?",
      created_at: new Date().toISOString(),
    },
  },
};

export const AssistantAnswerWithCitations: Story = {
  args: {
    message: {
      id: "msg-2",
      role: "assistant",
      content:
        "The `LLMRouter` is implemented in `backend/app/services/llm_router.py`. It establishes provider adapters for Gemini, Groq, NVIDIA, OpenRouter, and Ollama. When a primary provider returns a 429 quota failure or timeout, it records the failure in the fallback chain and immediately cascades to the next configured provider, with Ollama providing the final local offline guarantee.",
      sources: [
        {
          path: "backend/app/services/llm_router.py",
          symbol: "LLMRouter.generate_response",
          start_line: 142,
          end_line: 188,
          source_type: "indexed",
          language: "python",
          snippet: "async def generate_response(self, prompt, system_prompt): ...",
        },
        {
          path: "backend/app/services/llm_router.py",
          symbol: "OllamaAdapter",
          start_line: 95,
          end_line: 130,
          source_type: "live_mcp",
          language: "python",
          snippet: "class OllamaAdapter(BaseLLMAdapter): ...",
        },
      ],
      trace: {
        id: "trace-99",
        query: "Where is the LLMRouter implemented?",
        provider_used: "groq",
        model_used: "llama-3.3-70b-versatile",
        fallback_occurred: true,
        fallback_chain: [
          { provider: "gemini", model: "gemini-1.5-flash", status: "failed", error: "429 Quota Exceeded", latency_ms: 120 },
          { provider: "groq", model: "llama-3.3-70b-versatile", status: "success", latency_ms: 380 },
        ],
        mcp_invoked: true,
        mcp_tools_called: ["search_code"],
        retrieval_chunks_count: 4,
        latency_ms: 500,
        steps: [],
        created_at: new Date().toISOString(),
      },
      created_at: new Date().toISOString(),
    },
  },
};
