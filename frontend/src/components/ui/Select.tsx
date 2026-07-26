import { forwardRef, type SelectHTMLAttributes } from "react";

import { cn } from "@/utils/cn";

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  error?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, error, children, ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={cn(
          "h-11 w-full rounded-lg border bg-background px-3 text-sm",
          "focus-visible:outline-none focus-visible:ring-2",
          error
            ? "border-destructive focus-visible:ring-destructive"
            : "border-border focus-visible:ring-primary",
          className,
        )}
        {...props}
      >
        {children}
      </select>
    );
  },
);
Select.displayName = "Select";
