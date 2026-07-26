import { Link, useLocation, useNavigate } from "react-router-dom";
import { CalendarClock, FileText, HeartPulse, LayoutDashboard, Moon, Sun, User } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { cn } from "@/utils/cn";

const NAV_LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/appointments", label: "Appointments", icon: CalendarClock },
  { to: "/profile/patient", label: "Profile", icon: User },
];

export function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-lg">
      <nav className="container flex h-16 items-center justify-between gap-4">
        <Link to="/" className="flex shrink-0 items-center gap-2 font-bold text-primary">
          <HeartPulse className="h-6 w-6" aria-hidden="true" />
          <span className="hidden sm:inline">OncoNexus AI</span>
        </Link>

        {isAuthenticated && (
          <div className="hidden flex-1 items-center justify-center gap-1 md:flex">
            {NAV_LINKS.map(({ to, label, icon: Icon }) => {
              const isActive = location.pathname.startsWith(to);
              return (
                <Link
                  key={to}
                  to={to}
                  className={cn(
                    "flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  {label}
                </Link>
              );
            })}
          </div>
        )}

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Toggle dark mode"
            className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            {theme === "dark" ? (
              <Sun className="h-5 w-5" aria-hidden="true" />
            ) : (
              <Moon className="h-5 w-5" aria-hidden="true" />
            )}
          </button>

          {isAuthenticated ? (
            <>
              <span className="hidden text-sm text-muted-foreground lg:inline">
                {user?.full_name}
              </span>
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

      {isAuthenticated && (
        <div className="flex items-center gap-1 overflow-x-auto border-t border-border px-4 py-2 md:hidden">
          {NAV_LINKS.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className="flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted hover:text-foreground"
            >
              <Icon className="h-3.5 w-3.5" aria-hidden="true" />
              {label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}
