import type { Meta, StoryObj } from "@storybook/react";
import { Modal } from "../common/Modal";
import { Button } from "../common/Button";

const meta: Meta<typeof Modal> = {
  title: "Common/Modal",
  component: Modal,
};

export default meta;
type Story = StoryObj<typeof Modal>;

export const Default: Story = {
  args: {
    isOpen: true,
    title: "Register New Repository",
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
