import type { Meta, StoryObj } from "@storybook/react";
import { RepositorySelector } from "../ai/RepositorySelector";
import type { Repository } from "../../types";

const meta: Meta<typeof RepositorySelector> = {
  title: "AI/RepositorySelector",
  component: RepositorySelector,
  argTypes: {
    selectedRepoId: { control: "text" },
    loading: { control: "boolean" },
    disabled: { control: "boolean" },
    error: { control: "text" },
  },
};

export default meta;
type Story = StoryObj<typeof RepositorySelector>;

const sampleRepos: Repository[] = [
  {
    id: "repo-1",
    name: "octocat/Hello-World",
    url: "https://github.com/octocat/Hello-World",
    default_branch: "master",
    status: "indexed",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "repo-2",
    name: "facebook/react",
    url: "https://github.com/facebook/react",
    default_branch: "main",
    status: "indexing",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "repo-3",
    name: "tiangolo/fastapi",
    url: "https://github.com/tiangolo/fastapi",
    default_branch: "master",
    status: "unindexed",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

export const Default: Story = {
  args: {
    selectedRepoId: "repo-1",
    repositories: sampleRepos,
    onSelect: () => {},
    onAddClick: () => {},
  },
};

export const Loading: Story = {
  args: {
    selectedRepoId: null,
    repositories: [],
    loading: true,
    onSelect: () => {},
    onAddClick: () => {},
  },
};

export const Disabled: Story = {
  args: {
    selectedRepoId: "repo-1",
    repositories: sampleRepos,
    disabled: true,
    onSelect: () => {},
    onAddClick: () => {},
  },
};

export const WithError: Story = {
  args: {
    selectedRepoId: null,
    repositories: [],
    error: "Failed to fetch repositories from database. Connection refused.",
    onSelect: () => {},
    onAddClick: () => {},
  },
};

export const EmptyState: Story = {
  args: {
    selectedRepoId: null,
    repositories: [],
    onSelect: () => {},
    onAddClick: () => {},
  },
};
