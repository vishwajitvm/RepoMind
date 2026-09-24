import type { Meta, StoryObj } from "@storybook/react";
import { SourceCitation } from "../ai/SourceCitation";

const meta: Meta<typeof SourceCitation> = {
  title: "AI/SourceCitation",
  component: SourceCitation,
};

export default meta;
type Story = StoryObj<typeof SourceCitation>;

export const IndexedSource: Story = {
  args: {
    citation: {
      path: "backend/app/services/indexer.py",
      symbol: "RepositoryIndexer.index_repository",
      start_line: 25,
      end_line: 85,
      source_type: "indexed",
      language: "python",
      snippet: "async def index_repository(self, repository_id: str, job_id: str): ...",
    },
  },
};

export const LiveMCPSource: Story = {
  args: {
    citation: {
      path: "src/components/common/Button.tsx",
      symbol: "Button",
      start_line: 14,
      end_line: 52,
      source_type: "live_mcp",
      language: "typescript",
      snippet: "export const Button: React.FC<ButtonProps> = ({ children, variant ...",
    },
  },
};

export const WithoutSnippet: Story = {
  args: {
    citation: {
      path: "backend/Dockerfile",
      start_line: 1,
      end_line: 24,
      source_type: "indexed",
    },
  },
};
