import { Link, useNavigate } from "react-router-dom";
import { HeartPulse } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { useAuth } from "@/contexts/AuthContext";

export function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <header className="border-b border-border bg-background">
      <nav className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-primary">
          <HeartPulse className="h-6 w-6" aria-hidden="true" />
          <span>OncoNexus AI</span>
        </Link>

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <span className="hidden text-sm text-muted-foreground sm:inline">
                {user?.full_name}
              </span>
              <Link to="/dashboard" className="text-sm font-medium hover:text-primary">
                Dashboard
              </Link>
              <Button variant="outline" className="h-9 w-auto px-4" onClick={handleLogout}>
                Log out
              </Button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm font-medium hover:text-primary">
                Log in
              </Link>
              <Link to="/register">
                <Button className="h-9 w-auto px-4">Get started</Button>
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
