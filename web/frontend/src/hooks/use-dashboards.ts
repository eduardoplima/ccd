"use client";

import { useQuery } from "@tanstack/react-query";

import { getDashboardSummary } from "@/lib/dashboards-api";

export const dashboardsKeys = {
  all: ["dashboards"] as const,
  summary: (args: { topN: number }) => ["dashboards", "summary", args] as const,
};

export function useDashboardSummary({ topN = 10 }: { topN?: number } = {}) {
  return useQuery({
    queryKey: dashboardsKeys.summary({ topN }),
    queryFn: () => getDashboardSummary({ topN }),
  });
}
