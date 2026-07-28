import type { ComponentType } from "react";
import type { LucideProps } from "lucide-react";

import { Card } from "@/components/ui/Card";

interface GuidanceSectionCardProps {
  icon: ComponentType<LucideProps>;
  title: string;
  items: string[];
}

/** One category of guidance (e.g. "Nutrition guidance") rendered as its own
 * clearly-separated glass card with a bulleted list. Skips rendering
 * entirely when there are no items, so empty sections don't clutter the page. */
export function GuidanceSectionCard({ icon: Icon, title, items }: GuidanceSectionCardProps) {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <Card variant="glass" className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4 text-primary" aria-hidden="true" />
        <h3 className="text-sm font-semibold">{title}</h3>
      </div>
      <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </Card>
  );
}
