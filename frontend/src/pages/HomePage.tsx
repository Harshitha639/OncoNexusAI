import { useQuery } from "@tanstack/react-query";

import { fetchHealthStatus } from "@/services/healthService";

/**
 * Placeholder landing page — confirms the frontend/backend wiring works
 * by calling the health endpoint. Will be replaced by the real dashboard
 * once feature modules are implemented.
 */
export function HomePage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealthStatus,
  });

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-3xl font-bold text-primary">OncoNexus AI</h1>
      <p className="text-muted-foreground">
        Multi-Agent Intelligent Cancer Care Platform — project foundation initialized.
      </p>

      <div className="rounded-lg border border-border p-4">
        <h2 className="mb-2 text-lg font-semibold">Backend connectivity</h2>
        {isLoading && <p>Checking backend health...</p>}
        {isError && <p className="text-destructive">Could not reach the backend API.</p>}
        {data && (
          <pre className="rounded-md bg-muted p-3 text-sm">
            {JSON.stringify(data.data, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
