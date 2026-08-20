import { apiClient } from "@/lib/api-client";
import {
  DivergenciaDetail,
  Divergencias,
  DocumentoDetail,
  DocumentoListPage,
  Progresso,
  Span,
  divergenciaDetailSchema,
  divergenciasSchema,
  documentoDetailSchema,
  documentoListPageSchema,
  progressoSchema,
} from "@/schemas/dataset";

const BASE = "/api/v1/cgad/dataset";

// Filtro da aba aberta. Nas rotas de documento ele não escolhe o documento, e sim
// de qual fila vem o `proximo_pendente`.
export type FiltroFila = { comEntidades?: boolean; semAtosPessoal?: boolean };

function paramsFila({ comEntidades, semAtosPessoal }: FiltroFila) {
  return { com_entidades: comEntidades, sem_atos_pessoal: semAtosPessoal };
}

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

export async function getDocumento(id: number, filtro: FiltroFila = {}): Promise<DocumentoDetail> {
  const response = await apiClient.get(`${BASE}/documentos/${id}`, { params: paramsFila(filtro) });
  return documentoDetailSchema.parse(response.data);
}

export async function salvarAnotacao(
  id: number,
  body: { spans: Span[]; status: "pending" | "done" },
  filtro: FiltroFila = {},
): Promise<DocumentoDetail> {
  const response = await apiClient.put(`${BASE}/documentos/${id}/anotacao`, body, {
    params: paramsFila(filtro),
  });
  return documentoDetailSchema.parse(response.data);
}

export async function getProgresso(): Promise<Progresso> {
  const response = await apiClient.get(`${BASE}/progresso`);
  return progressoSchema.parse(response.data);
}

export async function getDivergencias(): Promise<Divergencias> {
  const response = await apiClient.get(`${BASE}/divergencias`);
  return divergenciasSchema.parse(response.data);
}

export async function getDivergenciaDetail(id: number): Promise<DivergenciaDetail> {
  const response = await apiClient.get(`${BASE}/divergencias/${id}`);
  return divergenciaDetailSchema.parse(response.data);
}
