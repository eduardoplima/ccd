import { apiClient } from "@/lib/api-client";
import {
  DocumentDetail,
  DocumentListPage,
  GroupDecisionRequest,
  GroupDecisionResponse,
  LabelsResponse,
  Progress,
  UnmappedDecisionRequest,
  UnmappedDecisionResponse,
  UnmappedListPage,
  documentDetailSchema,
  documentListPageSchema,
  groupDecisionResponseSchema,
  labelsResponseSchema,
  progressSchema,
  unmappedDecisionResponseSchema,
  unmappedListPageSchema,
} from "@/schemas/dataset-corrections";

const BASE = "/api/v1/cgad/admin/dataset-corrections";

export async function listDocuments({
  page = 1,
  pageSize = 20,
  onlyPending = false,
  minConfidence = 0,
}: {
  page?: number;
  pageSize?: number;
  onlyPending?: boolean;
  minConfidence?: number;
} = {}): Promise<DocumentListPage> {
  const response = await apiClient.get(`${BASE}/documents`, {
    params: {
      page,
      page_size: pageSize,
      only_pending: onlyPending,
      min_confidence: minConfidence,
    },
  });
  return documentListPageSchema.parse(response.data);
}

export async function getDocument(
  documentId: number,
  { minConfidence = 0 }: { minConfidence?: number } = {},
): Promise<DocumentDetail> {
  const response = await apiClient.get(`${BASE}/documents/${documentId}`, {
    params: { min_confidence: minConfidence },
  });
  return documentDetailSchema.parse(response.data);
}

export async function decideGroup(
  groupId: string,
  body: GroupDecisionRequest,
): Promise<GroupDecisionResponse> {
  const response = await apiClient.post(
    `${BASE}/groups/${encodeURIComponent(groupId)}/decide`,
    body,
  );
  return groupDecisionResponseSchema.parse(response.data);
}

export async function listUnmapped({
  page = 1,
  pageSize = 50,
  minConfidence = 0,
}: {
  page?: number;
  pageSize?: number;
  minConfidence?: number;
} = {}): Promise<UnmappedListPage> {
  const response = await apiClient.get(`${BASE}/unmapped`, {
    params: {
      page,
      page_size: pageSize,
      min_confidence: minConfidence,
    },
  });
  return unmappedListPageSchema.parse(response.data);
}

export async function decideUnmapped(
  rowId: number,
  body: UnmappedDecisionRequest,
): Promise<UnmappedDecisionResponse> {
  const response = await apiClient.post(`${BASE}/unmapped/${rowId}/decide`, body);
  return unmappedDecisionResponseSchema.parse(response.data);
}

export async function getProgress(): Promise<Progress> {
  const response = await apiClient.get(`${BASE}/progress`);
  return progressSchema.parse(response.data);
}

export async function getLabels(): Promise<LabelsResponse> {
  const response = await apiClient.get(`${BASE}/labels`);
  return labelsResponseSchema.parse(response.data);
}

export function exportUrl(): string {
  return `${apiClient.defaults.baseURL ?? ""}${BASE}/export`;
}
