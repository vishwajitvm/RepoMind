import type { Meta, StoryObj } from "@storybook/react";
import { ToolCall } from "../ai/ToolCall";

const meta: Meta<typeof ToolCall> = {
  title: "AI/ToolCall",
  component: ToolCall,
  argTypes: {
    toolName: { control: "text" },
    server: { control: "text" },
    status: {
      control: "select",
      options: ["idle", "running", "success", "error"],
    },
    latencyMs: { control: "number" },
    error: { control: "text" },
    expanded: { control: "boolean" },
  },
};

export default meta;
type Story = StoryObj<typeof ToolCall>;

export const Idle: Story = {
  args: {
    toolName: "get_file_contents",
    server: "github-mcp",
    status: "idle",
    args: { path: "README.md" },
  },
};

export const RunningSearchCode: Story = {
  args: {
    toolName: "search_code",
    server: "github-mcp",
    status: "running",
    args: { query: "LLMRouter repo:octocat/repomind" },
  },
};

export const SuccessGetFileContents: Story = {
  args: {
    toolName: "get_file_contents",
    server: "github-mcp",
    status: "success",
    latencyMs: 145,
    expanded: true,
    args: { path: "backend/app/services/llm_router.py", ref: "main" },
    output: { size: 4820, sha: "a1b2c3d4e5f6", branch: "master" },
  },
};

export const ErrorState: Story = {
  args: {
    toolName: "get_file_contents",
    server: "github-mcp",
    status: "error",
    latencyMs: 980,
    expanded: true,
    args: { path: "nonexistent/file.ts" },
    error: "GitHub API returned 404: Resource not found for path 'nonexistent/file.ts'",
  },
};
