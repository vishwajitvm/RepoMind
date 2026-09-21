import type { Meta, StoryObj } from "@storybook/react";
import { RepositorySelector } from "../ai/RepositorySelector";

const meta: Meta<typeof RepositorySelector> = {
  title: "AI/RepositorySelector",
  component: RepositorySelector,
};

export default meta;
type Story = StoryObj<typeof RepositorySelector>;

export const Default: Story = {
  args: {
    selectedRepoId: "repo-1",
    repositories: [
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
    ],
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
