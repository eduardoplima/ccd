import { apiClient } from "@/lib/api-client";
import { DashboardSummary, dashboardSummarySchema } from "@/schemas/dashboards";

export async function getDashboardSummary({
  topN = 10,
}: { topN?: number } = {}): Promise<DashboardSummary> {
  const response = await apiClient.get("/api/v1/cgad/dashboards/summary", {
    params: { top_n: topN },
  });
  return dashboardSummarySchema.parse(response.data);
}
