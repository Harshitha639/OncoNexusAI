import { QueryClient } from "@tanstack/react-query";

/**
 * Single shared TanStack Query client instance for the whole app.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 60_000,
    },
  },
});
