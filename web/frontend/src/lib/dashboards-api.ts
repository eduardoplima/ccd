import { apiClient } from "@/lib/api-client";
import { DashboardSummary, dashboardSummarySchema } from "@/schemas/dashboards";

type SummaryArgs = {
  startDate?: string; // YYYY-MM-DD
  endDate?: string;
  topN?: number;
};

export async function getDashboardSummary({
  startDate,
  endDate,
  topN = 10,
}: SummaryArgs = {}): Promise<DashboardSummary> {
  const response = await apiClient.get("/api/v1/cgad/dashboards/summary", {
    params: {
      start_date: startDate,
      end_date: endDate,
      top_n: topN,
    },
  });
  return dashboardSummarySchema.parse(response.data);
}
