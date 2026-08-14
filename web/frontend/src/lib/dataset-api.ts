import { apiClient } from "@/lib/api-client";
import {
  DocumentoDetail,
  DocumentoListPage,
  Progresso,
  Span,
  documentoDetailSchema,
  documentoListPageSchema,
  progressoSchema,
} from "@/schemas/dataset";

const BASE = "/api/v1/cgad/dataset";

export async function listDocumentos({
  page = 1,
  pageSize = 20,
  status,
  origem,
  ano,
  comEntidades,
  semAtosPessoal,
}: {
  page?: number;
  pageSize?: number;
  status?: string;
  origem?: string;
  ano?: number;
  comEntidades?: boolean;
  semAtosPessoal?: boolean;
} = {}): Promise<DocumentoListPage> {
  const response = await apiClient.get(`${BASE}/documentos`, {
    params: {
      page,
      page_size: pageSize,
      status,
      origem,
      ano,
      com_entidades: comEntidades,
      sem_atos_pessoal: semAtosPessoal,
    },
  });
  return documentoListPageSchema.parse(response.data);
}

export async function getDocumento(id: number): Promise<DocumentoDetail> {
  const response = await apiClient.get(`${BASE}/documentos/${id}`);
  return documentoDetailSchema.parse(response.data);
}

export async function salvarAnotacao(
  id: number,
  body: { spans: Span[]; status: "pending" | "done" },
): Promise<DocumentoDetail> {
  const response = await apiClient.put(`${BASE}/documentos/${id}/anotacao`, body);
  return documentoDetailSchema.parse(response.data);
}

export async function getProgresso(): Promise<Progresso> {
  const response = await apiClient.get(`${BASE}/progresso`);
  return progressoSchema.parse(response.data);
}
