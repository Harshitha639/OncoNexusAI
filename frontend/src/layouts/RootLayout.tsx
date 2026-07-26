import { Outlet } from "react-router-dom";

import { Navbar } from "@/components/common/Navbar";

/**
 * Base application shell shared by every route: a header with auth-aware
 * navigation, a soft gradient backdrop (for the glassmorphism cards used
 * throughout the patient dashboard), and a container for routed content.
 */
export function RootLayout() {
  return (
    <div className="relative flex min-h-screen flex-col bg-background text-foreground">
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,hsl(var(--primary)/0.15),transparent),radial-gradient(ellipse_60%_50%_at_100%_100%,hsl(var(--secondary)/0.12),transparent)]"
      />
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
