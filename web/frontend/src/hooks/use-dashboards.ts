"use client";

import { useQuery } from "@tanstack/react-query";

import { getDashboardSummary } from "@/lib/dashboards-api";

export const dashboardsKeys = {
  all: ["dashboards"] as const,
  summary: (args: { startDate?: string; endDate?: string; topN: number }) =>
    ["dashboards", "summary", args] as const,
};

export function useDashboardSummary({
  startDate,
  endDate,
  topN = 10,
}: {
  startDate?: string;
  endDate?: string;
  topN?: number;
} = {}) {
  return useQuery({
    queryKey: dashboardsKeys.summary({ startDate, endDate, topN }),
    queryFn: () => getDashboardSummary({ startDate, endDate, topN }),
  });
}
