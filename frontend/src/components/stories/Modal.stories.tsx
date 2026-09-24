import type { Meta, StoryObj } from "@storybook/react";
import { Modal } from "../common/Modal";
import { Button } from "../common/Button";

const meta: Meta<typeof Modal> = {
  title: "Common/Modal",
  component: Modal,
  argTypes: {
    isOpen: { control: "boolean" },
    title: { control: "text" },
    size: {
      control: "select",
      options: ["sm", "md", "lg", "xl"],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Modal>;

export const Default: Story = {
  args: {
    isOpen: true,
    title: "Register New Repository",
    size: "md",
    children: (
      <div className="flex flex-col gap-4">
        <p className="text-sm text-gray-300">
          Enter GitHub repository URL to initiate shallow clone and AST-based chunking.
        </p>
        <div className="flex justify-end gap-2 pt-3 border-t border-border">
          <Button variant="secondary" size="sm">Cancel</Button>
          <Button variant="primary" size="sm">Start Indexing</Button>
        </div>
      </div>
    ),
  },
};

export const SmallConfirmation: Story = {
  args: {
    isOpen: true,
    title: "Delete Repository Index",
    size: "sm",
    children: (
      <div className="flex flex-col gap-4">
        <p className="text-xs text-gray-300">
          Are you sure you want to purge all Qdrant vectors and SQLite indexing metadata?
        </p>
        <div className="flex justify-end gap-2 pt-3 border-t border-border">
          <Button variant="secondary" size="sm">Cancel</Button>
          <Button variant="danger" size="sm">Purge Data</Button>
        </div>
      </div>
    ),
  },
};

export const LargeTraceView: Story = {
  args: {
    isOpen: true,
    title: "LangGraph Execution Inspection",
    size: "lg",
    children: (
      <div className="flex flex-col gap-3 font-mono text-xs">
        <p className="text-gray-300">Detailed multi-node execution state:</p>
        <div className="p-3 bg-surface-raised rounded border border-border text-gray-300">
          <pre>{`Node: retrieve_step (Qdrant) -> 5 chunks matched (local embeddings, 18ms)
Node: mcp_decision_step -> False
Node: llm_generate_step -> Groq Llama-3.3-70B (380ms)`}</pre>
        </div>
      </div>
    ),
  },
};
