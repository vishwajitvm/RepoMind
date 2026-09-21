import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "../common/Badge";
import { Check, ShieldCheck, AlertCircle } from "lucide-react";

const meta: Meta<typeof Badge> = {
  title: "Common/Badge",
  component: Badge,
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "success", "warning", "danger", "neutral"],
    },
    size: {
      control: "select",
      options: ["sm", "md"],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Badge>;

export const Success: Story = {
  args: {
    children: "Indexed (100%)",
    variant: "success",
    icon: <Check className="w-3 h-3" />,
  },
};

export const LiveMCP: Story = {
  args: {
    children: "Live MCP Verified",
    variant: "primary",
    icon: <ShieldCheck className="w-3 h-3" />,
  },
};

export const Warning: Story = {
  args: {
    children: "Fallback: Ollama",
    variant: "warning",
  },
};

export const Danger: Story = {
  args: {
    children: "Failed (Rate Limited)",
    variant: "danger",
    icon: <AlertCircle className="w-3 h-3" />,
  },
};
