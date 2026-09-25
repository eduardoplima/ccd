"use client";

import { useQuery } from "@tanstack/react-query";

import { getMultasNaoCominadas } from "@/lib/multas-nao-cominadas-api";

export const multasNaoCominadasKeys = {
  all: ["multas-nao-cominadas"] as const,
};

export function useMultasNaoCominadas() {
  return useQuery({
    queryKey: multasNaoCominadasKeys.all,
    queryFn: getMultasNaoCominadas,
  });
}
