import { Link, Outlet } from "react-router-dom";
import { HeartPulse } from "lucide-react";

/**
 * Centered, card-based layout used by login/register/forgot-password pages.
 */
export function AuthLayout() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-muted/40 px-4 py-12">
      <div className="w-full max-w-md">
        <Link
          to="/"
          className="mb-6 flex items-center justify-center gap-2 text-lg font-bold text-primary"
        >
          <HeartPulse className="h-6 w-6" aria-hidden="true" />
          OncoNexus AI
        </Link>
        <Outlet />
      </div>
    </div>
  );
}
