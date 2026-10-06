"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import { executarJob, listarJobs } from "@/lib/api/admin-jobs";

export function useAdminJobs() {
  return useQuery({ queryKey: ["admin-jobs"], queryFn: listarJobs });
}

export function useExecutarJob() {
  return useMutation({ mutationFn: executarJob });
}
