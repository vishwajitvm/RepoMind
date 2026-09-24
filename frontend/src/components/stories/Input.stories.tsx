import type { Meta, StoryObj } from "@storybook/react";
import { Input } from "../common/Input";
import { Search, Github } from "lucide-react";

const meta: Meta<typeof Input> = {
  title: "Common/Input",
  component: Input,
  argTypes: {
    label: { control: "text" },
    placeholder: { control: "text" },
    value: { control: "text" },
    error: { control: "text" },
    helperText: { control: "text" },
    disabled: { control: "boolean" },
    required: { control: "boolean" },
  },
};

export default meta;
type Story = StoryObj<typeof Input>;

export const Default: Story = {
  args: {
    label: "GitHub Repository URL",
    placeholder: "https://github.com/owner/repository",
    icon: <Github className="w-4 h-4" />,
    helperText: "HTTPS clone URL of public or authenticated repository.",
  },
};

export const WithError: Story = {
  args: {
    label: "Branch Name",
    value: "invalid branch name!",
    error: "Branch name contains invalid characters.",
  },
};

export const Disabled: Story = {
  args: {
    label: "Repository ID",
    value: "cbee282e-bad2-4603-b556-9256fddf1b2f",
    disabled: true,
    helperText: "Immutable UUID generated during registration.",
  },
};

export const SearchInput: Story = {
  args: {
    placeholder: "Search code chunks...",
    icon: <Search className="w-4 h-4" />,
  },
};
