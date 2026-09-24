import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "../common/Button";
import { Sparkles, Trash2, ArrowRight } from "lucide-react";

const meta: Meta<typeof Button> = {
  title: "Common/Button",
  component: Button,
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "danger", "ghost", "outline"],
    },
    size: {
      control: "select",
      options: ["sm", "md", "lg"],
    },
    loading: { control: "boolean" },
    disabled: { control: "boolean" },
    fullWidth: { control: "boolean" },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    children: "Ask RepoMind",
    variant: "primary",
    size: "md",
    icon: <Sparkles className="w-4 h-4" />,
  },
};

export const Loading: Story = {
  args: {
    children: "Indexing Repository...",
    variant: "primary",
    loading: true,
  },
};

export const Secondary: Story = {
  args: {
    children: "Cancel",
    variant: "secondary",
  },
};

export const Danger: Story = {
  args: {
    children: "Delete Index",
    variant: "danger",
    icon: <Trash2 className="w-4 h-4" />,
  },
};

export const OutlineWithRightIcon: Story = {
  args: {
    children: "View Full Trace",
    variant: "outline",
    icon: <ArrowRight className="w-4 h-4" />,
    iconPosition: "right",
  },
};

export const Disabled: Story = {
  args: {
    children: "Unavailable Action",
    variant: "primary",
    disabled: true,
  },
};

export const Ghost: Story = {
  args: {
    children: "Dismiss Details",
    variant: "ghost",
  },
};

export const FullWidth: Story = {
  args: {
    children: "Trigger Repository Re-indexing",
    variant: "primary",
    fullWidth: true,
  },
};
