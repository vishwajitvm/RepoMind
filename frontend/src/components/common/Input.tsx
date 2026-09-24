import React, { forwardRef } from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, icon, className, id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-xs font-semibold text-gray-300">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {icon && (
            <div className="absolute left-3 text-gray-400 pointer-events-none shrink-0">
              {icon}
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            className={twMerge(
              clsx(
                "w-full bg-surface border rounded-lg py-2 text-sm text-gray-100 placeholder-gray-500 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500/50",
                icon ? "pl-9 pr-3.5" : "px-3.5",
                error
                  ? "border-red-500 focus:border-red-500 focus:ring-red-500/30"
                  : "border-border hover:border-zinc-600 focus:border-emerald-500",
                className
              )
            )}
            {...props}
          />
        </div>
        {error && <p className="text-xs text-red-400 font-medium">{error}</p>}
        {!error && helperText && <p className="text-xs text-gray-400">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";
