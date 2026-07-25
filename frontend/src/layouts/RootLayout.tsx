import { Outlet } from "react-router-dom";

import { Navbar } from "@/components/common/Navbar";

/**
 * Base application shell shared by every route: a header with auth-aware
 * navigation, and a container for the routed page content.
 */
export function RootLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
