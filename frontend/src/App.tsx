import { AppRoutes } from "@/routes";

/**
 * Root application component.
 *
 * Kept intentionally minimal — providers live in `main.tsx`, route
 * definitions live in `routes/`, and page-level logic lives under `pages/`.
 */
function App() {
  return <AppRoutes />;
}

export default App;
