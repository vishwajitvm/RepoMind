import type { Meta, StoryObj } from "@storybook/react";
import { ToolCall } from "../ai/ToolCall";

const meta: Meta<typeof ToolCall> = {
  title: "AI/ToolCall",
  component: ToolCall,
  argTypes: {
    status: {
      control: "select",
      options: ["idle", "running", "success", "error"],
    },
  },
};

export default meta;
type Story = StoryObj<typeof ToolCall>;

export const RunningSearchCode: Story = {
  args: {
    toolName: "GitHub MCP → search_code",
    status: "running",
    args: { query: "LLMRouter repo:octocat/repomind" },
  },
};

export const SuccessGetFileContents: Story = {
  args: {
    toolName: "GitHub MCP → get_file_contents",
    status: "success",
    latencyMs: 145,
    args: { path: "backend/app/services/llm_router.py", ref: "main" },
    output: { size: 4820, sha: "a1b2c3d4e5f6" },
  },
};

export const ErrorState: Story = {
  args: {
    toolName: "GitHub MCP → get_file_contents",
    status: "error",
    latencyMs: 980,
    args: { path: "nonexistent/file.ts" },
    output: "404 Not Found from GitHub API",
  },
};
