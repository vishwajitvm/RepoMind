import type { Meta, StoryObj } from "@storybook/react";
import { Textarea } from "../common/Textarea";

const meta: Meta<typeof Textarea> = {
  title: "Common/Textarea",
  component: Textarea,
};

export default meta;
type Story = StoryObj<typeof Textarea>;

export const Default: Story = {
  args: {
    label: "Custom System Prompt",
    placeholder: "Provide custom instructions for code inspection...",
    rows: 4,
    helperText: "Appended to LangGraph LLM generation node.",
  },
};

export const WithError: Story = {
  args: {
    label: "Repository Description",
    value: "Too short",
    error: "Description must be at least 10 characters.",
  },
};
