import type { Meta, StoryObj } from "@storybook/react";
import { Spinner } from "../common/Spinner";

const meta: Meta<typeof Spinner> = {
  title: "Common/Spinner",
  component: Spinner,
  argTypes: {
    size: {
      control: "select",
      options: ["sm", "md", "lg"],
    },
    color: { control: "color" },
  },
};

export default meta;
type Story = StoryObj<typeof Spinner>;

export const Default: Story = {
  args: {
    size: "md",
    color: "#10b981",
  },
};

export const Small: Story = {
  args: {
    size: "sm",
    color: "#10b981",
  },
};

export const Large: Story = {
  args: {
    size: "lg",
    color: "#38bdf8",
  },
};
