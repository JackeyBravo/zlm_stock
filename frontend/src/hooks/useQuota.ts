import useSWR from "swr";
import { fetcher } from "../lib/api";
import type { QuotaResponse } from "../types/common";

export function useQuota() {
  const { data, error, isLoading, mutate } = useSWR<QuotaResponse>("/quota", fetcher, {
    refreshInterval: 60_000,
  });

  return {
    quota: data,
    isLoading,
    error,
    refresh: mutate,
  };
}

