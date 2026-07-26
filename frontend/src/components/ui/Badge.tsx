import type { HTMLAttributes } from "react";

import { cn } from "@/utils/cn";

export type BadgeVariant = "default" | "success" | "warning" | "destructive" | "info";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: "bg-muted text-muted-foreground",
  success: "bg-secondary/15 text-secondary",
  warning: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
  destructive: "bg-destructive/15 text-destructive",
  info: "bg-primary/15 text-primary",
};

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium capitalize",
        variantClasses[variant],
        className,
      )}
      {...props}
    />
  );
}
