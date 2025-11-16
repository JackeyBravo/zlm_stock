import { useState } from "react";
import { apiClient } from "../lib/api";
import type { RandomPickResponse } from "../types/common";

export function useRandomPick() {
  const [data, setData] = useState<RandomPickResponse | null>(null);
  const [isLoading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRandom = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get<RandomPickResponse>("/random");
      setData(response.data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return { randomPick: data, isLoading, error, fetchRandom };
}

