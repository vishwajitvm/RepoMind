import type { Meta, StoryObj } from "@storybook/react";
import { ChatInput } from "../ai/ChatInput";

const meta: Meta<typeof ChatInput> = {
  title: "AI/ChatInput",
  component: ChatInput,
  argTypes: {
    placeholder: { control: "text" },
    disabled: { control: "boolean" },
    loading: { control: "boolean" },
  },
};

export default meta;
type Story = StoryObj<typeof ChatInput>;

export const Default: Story = {
  args: {
    placeholder: "Ask anything about this codebase...",
    disabled: false,
    loading: false,
  },
};

export const Loading: Story = {
  args: {
    placeholder: "LangGraph synthesizing answer...",
    disabled: true,
    loading: true,
  },
};

export const Disabled: Story = {
  args: {
    placeholder: "Please select a repository on the left first",
    disabled: true,
    loading: false,
  },
};
