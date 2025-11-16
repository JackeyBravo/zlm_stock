import useSWR from "swr";
import { fetcher } from "../lib/api";
import type { RankResponse } from "../types/common";

export function useRank(type: "hot" | "best" | "worst", days = 10, limit = 20, k = 5) {
  const params = new URLSearchParams({
    days: String(days),
    limit: String(limit),
  });
  if (type !== "hot") {
    params.append("k", String(k));
  }
  const url = `/rank/${type}?${params.toString()}`;
  return useSWR<RankResponse>(url, fetcher);
}

