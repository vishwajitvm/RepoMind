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
    title: { control: "text" },
    message: { control: "text" },
    duration: { control: "number" },
  },
};

export default meta;
type Story = StoryObj<typeof Toast>;

export const Info: Story = {
  args: {
    type: "info",
    title: "Indexing Dispatched",
    message: "Background job #12 queued in Redis. Worker processing repository files.",
  },
};

export const Success: Story = {
  args: {
    type: "success",
    title: "Qdrant Index Synchronized",
    message: "Repository indexing completed: 142 code chunks stored in Qdrant.",
  },
};

export const FallbackWarning: Story = {
  args: {
    type: "warning",
    title: "Automatic Provider Fallback",
    message: "Gemini rate limited; automatically fell back to Groq Llama-3.3-70B.",
  },
};

export const Error: Story = {
  args: {
    type: "error",
    title: "MCP Warning",
    message: "GitHub MCP connection timed out. Using indexed source as fallback.",
  },
};

export const WithAutoDismiss: Story = {
  args: {
    type: "info",
    title: "Transient Status",
    message: "This notification will auto-dismiss after 5000ms.",
    duration: 5000,
    onClose: () => alert("Auto-dismissed or closed!"),
  },
};
