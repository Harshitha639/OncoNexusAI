import { forwardRef, type InputHTMLAttributes } from "react";

import { cn } from "@/utils/cn";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "h-11 w-full rounded-lg border bg-background px-3 text-sm",
          "placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2",
          error
            ? "border-destructive focus-visible:ring-destructive"
            : "border-border focus-visible:ring-primary",
          className,
        )}
        {...props}
      />
    );
  },
);
Input.displayName = "Input";
