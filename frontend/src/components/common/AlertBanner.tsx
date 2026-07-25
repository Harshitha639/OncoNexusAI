import { cn } from "@/utils/cn";

interface AlertBannerProps {
  message: string;
  variant?: "error" | "success" | "info";
}

const variantClasses: Record<NonNullable<AlertBannerProps["variant"]>, string> = {
  error: "border-destructive/30 bg-destructive/10 text-destructive",
  success: "border-secondary/30 bg-secondary/10 text-secondary",
  info: "border-primary/30 bg-primary/10 text-primary",
};

export function AlertBanner({ message, variant = "info" }: AlertBannerProps) {
  return (
    <div
      role="alert"
      className={cn("rounded-lg border px-4 py-3 text-sm", variantClasses[variant])}
    >
      {message}
    </div>
  );
}
