import { useState, useCallback, useEffect } from "react";
import { apiClient } from "@/lib/api/client";

interface FetchOptions {
  requireAuth?: boolean;
  lazy?: boolean;
  fallbackData?: any;
}

/**
 * A zero-dependency custom hook for fetching and caching data from the backend.
 * Replaces the need for external libraries like SWR or React Query for basic needs.
 */
export function useDataFetch<T>(endpoint: string, options: FetchOptions = {}) {
  const [data, setData] = useState<T | null>(options.fallbackData || null);
  const [isLoading, setIsLoading] = useState(!options.lazy);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Intentionally simulating a realistic network delay for UI testing if mock data is used
      // Remove this when real API is fully verified
      if (options.fallbackData && process.env.NODE_ENV === "development") {
        await new Promise((resolve) => setTimeout(resolve, 800));
        setData(options.fallbackData);
        setIsLoading(false);
        return options.fallbackData;
      }

      const result = await apiClient<T>(endpoint, {
        method: "GET",
        requireAuth: options.requireAuth ?? true,
      });

      setData(result);
      return result;
    } catch (err: any) {
      if (options.fallbackData) {
         // Silently fallback to mock data if the backend isn't ready
         console.warn(`[useDataFetch] Failed to fetch ${endpoint}, using fallback data.`);
         setData(options.fallbackData);
      } else {
         setError(err);
      }
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [endpoint, options.requireAuth, options.fallbackData]);

  useEffect(() => {
    if (!options.lazy) {
      fetchData().catch(() => {});
    }
  }, [fetchData, options.lazy]);

  const mutate = useCallback((newData: T | ((prev: T | null) => T)) => {
    setData((prev) => (typeof newData === "function" ? (newData as Function)(prev) : newData));
  }, []);

  return { data, isLoading, error, mutate, refetch: fetchData };
}
