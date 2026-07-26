import type { HTMLAttributes } from "react";

import { cn } from "@/utils/cn";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "solid" | "glass";
}

export function Card({ className, variant = "solid", ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl p-8",
        variant === "solid" && "border border-border bg-background shadow-sm",
        variant === "glass" && "glass-card p-6",
        className,
      )}
      {...props}
    />
  );
}
