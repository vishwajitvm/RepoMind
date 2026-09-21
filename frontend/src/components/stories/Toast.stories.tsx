import type { Meta, StoryObj } from "@storybook/react";
import { Toast } from "../common/Toast";

const meta: Meta<typeof Toast> = {
  title: "Common/Toast",
  component: Toast,
  argTypes: {
    type: {
      control: "select",
      options: ["info", "success", "warning", "error"],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Toast>;

export const Success: Story = {
  args: {
    type: "success",
    message: "Repository indexing completed: 142 code chunks stored in Qdrant.",
  },
};

export const FallbackWarning: Story = {
  args: {
    type: "warning",
    message: "Gemini rate limited; automatically fell back to Groq Llama-3.3-70B.",
  },
};

export const Error: Story = {
  args: {
    type: "error",
    message: "GitHub MCP connection timed out. Using indexed source as fallback.",
  },
};
