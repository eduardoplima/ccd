"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  decideGroup,
  decideUnmapped,
  getDocument,
  getLabels,
  getProgress,
  listDocuments,
  listUnmapped,
} from "@/lib/dataset-corrections-api";
import {
  GroupDecisionRequest,
  UnmappedDecisionRequest,
} from "@/schemas/dataset-corrections";

export const datasetCorrectionsKeys = {
  all: ["dataset-corrections"] as const,
  documents: (args: {
    page: number;
    pageSize: number;
    onlyPending: boolean;
    minConfidence: number;
  }) => ["dataset-corrections", "documents", args] as const,
  document: (id: number, minConfidence: number) =>
    ["dataset-corrections", "documents", id, { minConfidence }] as const,
  unmapped: (args: {
    page: number;
    pageSize: number;
    minConfidence: number;
  }) => ["dataset-corrections", "unmapped", args] as const,
  progress: () => ["dataset-corrections", "progress"] as const,
  labels: () => ["dataset-corrections", "labels"] as const,
};

export function useDocuments(args: {
  page?: number;
  pageSize?: number;
  onlyPending?: boolean;
  minConfidence?: number;
} = {}) {
  const page = args.page ?? 1;
  const pageSize = args.pageSize ?? 20;
  const onlyPending = args.onlyPending ?? false;
  const minConfidence = args.minConfidence ?? 0;
  return useQuery({
    queryKey: datasetCorrectionsKeys.documents({
      page,
      pageSize,
      onlyPending,
      minConfidence,
    }),
    queryFn: () =>
      listDocuments({ page, pageSize, onlyPending, minConfidence }),
  });
}

export function useDocumentDetail(
  documentId: number,
  { minConfidence = 0 }: { minConfidence?: number } = {},
) {
  return useQuery({
    queryKey: datasetCorrectionsKeys.document(documentId, minConfidence),
    queryFn: () => getDocument(documentId, { minConfidence }),
    enabled: Number.isFinite(documentId),
  });
}

export function useUnmapped(args: {
  page?: number;
  pageSize?: number;
  minConfidence?: number;
} = {}) {
  const page = args.page ?? 1;
  const pageSize = args.pageSize ?? 50;
  const minConfidence = args.minConfidence ?? 0;
  return useQuery({
    queryKey: datasetCorrectionsKeys.unmapped({
      page,
      pageSize,
      minConfidence,
    }),
    queryFn: () => listUnmapped({ page, pageSize, minConfidence }),
  });
}

export function useProgress() {
  return useQuery({
    queryKey: datasetCorrectionsKeys.progress(),
    queryFn: getProgress,
    staleTime: 5_000,
  });
}

export function useLabels() {
  return useQuery({
    queryKey: datasetCorrectionsKeys.labels(),
    queryFn: getLabels,
    staleTime: Infinity,
  });
}

export function useDecideGroup(documentId: number | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      groupId,
      body,
    }: {
      groupId: string;
      body: GroupDecisionRequest;
    }) => decideGroup(groupId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: datasetCorrectionsKeys.progress(),
      });
      queryClient.invalidateQueries({
        queryKey: ["dataset-corrections", "documents"],
      });
      if (documentId !== null) {
        queryClient.invalidateQueries({
          queryKey: ["dataset-corrections", "documents", documentId],
        });
      }
    },
  });
}

export function useDecideUnmapped() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      rowId,
      body,
    }: {
      rowId: number;
      body: UnmappedDecisionRequest;
    }) => decideUnmapped(rowId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: datasetCorrectionsKeys.progress(),
      });
      queryClient.invalidateQueries({
        queryKey: ["dataset-corrections", "unmapped"],
      });
    },
  });
}
