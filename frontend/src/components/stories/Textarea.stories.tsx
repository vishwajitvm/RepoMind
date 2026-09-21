import type { Meta, StoryObj } from "@storybook/react";
import { Textarea } from "../common/Textarea";

const meta: Meta<typeof Textarea> = {
  title: "Common/Textarea",
  component: Textarea,
  argTypes: {
    label: { control: "text" },
    placeholder: { control: "text" },
    value: { control: "text" },
    error: { control: "text" },
    helperText: { control: "text" },
    rows: { control: "number" },
    disabled: { control: "boolean" },
    maxLength: { control: "number" },
  },
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

export const Disabled: Story = {
  args: {
    label: "Read-Only AST Dump",
    value: "class LLMRouter:\n    def __init__(self):\n        pass",
    rows: 3,
    disabled: true,
  },
};

export const LongContent: Story = {
  args: {
    label: "Code Chunk Snippet",
    value: `async def generate_response(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 1500,
    temperature: float = 0.2
) -> Tuple[str, str, str, bool, List[Dict[str, Any]]]:
    fallback_chain = []
    for adapter in self.adapters:
        try:
            return await adapter.generate(prompt)
        except Exception as e:
            fallback_chain.append({"provider": adapter.provider_name, "error": str(e)})`,
    rows: 8,
    helperText: "Preserves AST metadata and line numbers.",
  },
};
