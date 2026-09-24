import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface BadgeProps {
  variant?: "primary" | "success" | "warning" | "danger" | "neutral";
  size?: "sm" | "md";
  children: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = "neutral",
  size = "md",
  children,
  icon,
  className,
}) => {
  const baseStyles = "inline-flex items-center font-medium rounded-full shrink-0 select-none";

  const sizeStyles = {
    sm: "text-[10px] px-2 py-0.5 gap-1",
    md: "text-xs px-2.5 py-1 gap-1.5",
  };

  const variantStyles = {
    primary: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
    success: "bg-green-500/15 text-green-400 border border-green-500/30",
    warning: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
    danger: "bg-red-500/15 text-red-400 border border-red-500/30",
    neutral: "bg-zinc-800 text-zinc-300 border border-border",
  };

  return (
    <span
      className={twMerge(
        clsx(baseStyles, sizeStyles[size], variantStyles[variant], className)
      )}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </span>
  );
};
