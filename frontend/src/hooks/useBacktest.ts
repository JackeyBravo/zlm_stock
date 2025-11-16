import useSWR from "swr";
import { apiClient, fetcher } from "../lib/api";
import type { BacktestResponse } from "../types/backtest";

export function useBacktest(btId?: string) {
  const shouldFetch = Boolean(btId);
  const { data, error, isLoading, mutate } = useSWR<BacktestResponse>(
    shouldFetch ? `/backtest/${btId}` : null,
    fetcher,
  );
  return { backtest: data, error, isLoading, refresh: mutate };
}

export async function createBacktest(payload: Record<string, unknown>) {
  const response = await apiClient.post<BacktestResponse>("/backtest", payload);
  return response.data;
}

