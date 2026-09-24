import React, { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { Button } from "../common/Button";

export interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  loading?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  disabled = false,
  loading = false,
  placeholder = "Ask anything about this codebase...",
}) => {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || disabled || loading) return;
    onSend(text.trim());
    setText("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        180
      )}px`;
    }
  }, [text]);

  return (
    <form
      onSubmit={handleSubmit}
      className="relative flex items-end gap-2 bg-surface border border-border rounded-xl p-2 focus-within:border-emerald-500/80 focus-within:ring-2 focus-within:ring-emerald-500/20 transition-all shadow-md"
    >
      <textarea
        ref={textareaRef}
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled || loading}
        className="w-full bg-transparent px-3 py-1.5 text-sm text-gray-100 placeholder-gray-500 resize-none focus:outline-none max-h-44 disabled:opacity-50"
      />
      <Button
        type="submit"
        variant="primary"
        size="sm"
        disabled={!text.trim() || disabled}
        loading={loading}
        icon={<Send className="w-4 h-4" />}
        aria-label="Send message"
        className="rounded-lg h-9 w-9 p-0 shrink-0"
      />
    </form>
  );
};
