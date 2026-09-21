import type { Meta, StoryObj } from "@storybook/react";
import { Select } from "../common/Select";

const meta: Meta<typeof Select> = {
  title: "Common/Select",
  component: Select,
};

export default meta;
type Story = StoryObj<typeof Select>;

export const Default: Story = {
  args: {
    label: "LLM Router Priority",
    options: [
      { value: "gemini", label: "Google Gemini 1.5 Flash (Cloud)" },
      { value: "groq", label: "Groq Llama 3.3 70B (Fast Cloud)" },
      { value: "ollama", label: "Ollama DeepSeek-R1 (Local Fallback)" },
    ],
  },
};

export const WithError: Story = {
  args: {
    label: "Embedding Dimension",
    options: [
      { value: "384", label: "384 (Default Dense)" },
      { value: "768", label: "768 (High Dimensional)" },
    ],
    error: "Selected model does not support 768 dimensions.",
  },
};
