import type { Meta, StoryObj } from "@storybook/react";
import { Select } from "../common/Select";

const meta: Meta<typeof Select> = {
  title: "Common/Select",
  component: Select,
  argTypes: {
    label: { control: "text" },
    placeholder: { control: "text" },
    value: { control: "text" },
    error: { control: "text" },
    helperText: { control: "text" },
    disabled: { control: "boolean" },
  },
};

export default meta;
type Story = StoryObj<typeof Select>;

export const Default: Story = {
  args: {
    label: "LLM Router Priority",
    options: [
      { value: "gemini", label: "Google Gemini 1.5 Flash (Cloud)" },
      { value: "groq", label: "Groq Llama 3.3 70B (Fast Cloud)" },
      { value: "openai", label: "OpenAI GPT-4o-mini (Cloud)" },
      { value: "ollama", label: "Ollama DeepSeek-R1 (Local Fallback)" },
    ],
  },
};

export const WithPlaceholder: Story = {
  args: {
    label: "Embedding Provider",
    placeholder: "-- Select Provider --",
    options: [
      { value: "local", label: "Local Dense Normalized (Default)" },
      { value: "gemini", label: "Gemini text-embedding-004" },
      { value: "openai", label: "OpenAI text-embedding-3-small" },
      { value: "ollama", label: "Ollama nomic-embed-text" },
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

export const Disabled: Story = {
  args: {
    label: "Vector Index Mode",
    disabled: true,
    options: [
      { value: "hnsw", label: "HNSW (Locked by Qdrant schema)" },
    ],
    helperText: "Configured statically in Settings.",
  },
};
