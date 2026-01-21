"use client";

import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { useState } from "react";

interface Props {
  children: React.ReactNode;
}

export default function QueryProvider({ children }: Props) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            retry: (failureCount, error: any) => {
              // Don't retry on auth errors
              if (error?.status === 401 || error?.status === 403) {
                return false;
              }
              // Retry other errors up to 2 times
              return failureCount < 2;
            },
          },
          mutations: {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            onError: (error: any) => {
              console.error("Mutation error:", error);
            },
          },
        },
      }),
  );
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
