import { forwardRef, type TextareaHTMLAttributes } from "react";

import { cn } from "@/utils/cn";

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <textarea
        ref={ref}
        rows={4}
        className={cn(
          "w-full rounded-lg border bg-background px-3 py-2 text-sm",
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
Textarea.displayName = "Textarea";
