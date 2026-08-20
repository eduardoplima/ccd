import { Pessoa, SolidarioMulta, TipoEntidade } from "@/schemas/review";

// O extrator devolve nomes com sufixo de cargo — "NEREU BATISTA LINHARES
// (PRESIDENTE)" — que precisam casar com a pessoa do processo "Nereu Batista
// Linhares" para herdar o CPF.
export function normalizeNome(s: string): string {
  return s
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/\(.*?\)/g, " ")
    .replace(/[^a-zA-Z\s]/g, " ")
    .toUpperCase()
    .replace(/\s+/g, " ")
    .trim();
}

/** Pessoa do processo cujo nome normalizado bate com o proposto — só quando o
 * casamento é único (homônimos ficam para o revisor decidir). */
export function matchPessoa(nome: unknown, pessoas: Pessoa[]): Pessoa | null {
  if (typeof nome !== "string" || !nome.trim()) return null;
  const alvo = normalizeNome(nome);
  if (!alvo) return null;
  const candidatas = pessoas.filter((p) => normalizeNome(p.nome) === alvo);
  return candidatas.length === 1 ? candidatas[0] : null;
}

/** Gestor = pessoa com cargo registrado no Anexo 42 (registro oficial de
 * gestores da unidade jurisdicionada). */
export function isGestor(p: Pessoa): boolean {
  return p.cargos.some((c) => c.fonte === "anexo42");
}

type CampoResponsavel = {
  nome: string;
  documento: string | null;
  solidarios: string | null;
};

const CAMPOS_RESPONSAVEL: Record<TipoEntidade, CampoResponsavel[]> = {
  multa: [
    { nome: "nome_responsavel", documento: "documento_responsavel", solidarios: "solidarios" },
  ],
  obrigacao: [
    {
      nome: "nome_responsavel_multa_cominatoria",
      documento: "documento_responsavel_multa_cominatoria",
      solidarios: "solidarios_multa_cominatoria",
    },
  ],
  recomendacao: [{ nome: "nome_responsavel", documento: null, solidarios: null }],
  ressarcimento: [
    { nome: "nome_responsavel", documento: "documento_responsavel", solidarios: null },
  ],
};

/** Vincula os responsáveis propostos às pessoas do processo: canoniza o nome e
 * preenche o documento quando ainda vazio. Não mexe onde já há documento.
 * Responsável vazio na extração é pré-preenchido com o gestor do Anexo 42,
 * quando há exatamente um (ambíguo fica para o revisor). */
export function vincularPessoas(
  tipo: TipoEntidade,
  campos: Record<string, unknown>,
  pessoas: Pessoa[],
): Record<string, unknown> {
  const out = { ...campos };
  const gestores = pessoas.filter(isGestor);
  for (const campo of CAMPOS_RESPONSAVEL[tipo]) {
    // Na obrigação o responsável é o da multa cominatória — só existe se ela existir.
    const aplicavel = tipo !== "obrigacao" || !!out.tem_multa_cominatoria;
    const nomeAtual = out[campo.nome];
    if (aplicavel && (typeof nomeAtual !== "string" || !nomeAtual.trim()) && gestores.length === 1) {
      out[campo.nome] = gestores[0].nome;
      if (campo.documento && gestores[0].documento) out[campo.documento] = gestores[0].documento;
      continue;
    }
    const documentoAtual = campo.documento ? out[campo.documento] : null;
    const pessoa = matchPessoa(out[campo.nome], pessoas);
    if (pessoa && !documentoAtual) {
      out[campo.nome] = pessoa.nome;
      if (campo.documento && pessoa.documento) out[campo.documento] = pessoa.documento;
    }
    if (campo.solidarios && Array.isArray(out[campo.solidarios])) {
      out[campo.solidarios] = (out[campo.solidarios] as SolidarioMulta[]).map((row) => {
        if (row.documento) return row;
        const p = matchPessoa(row.nome, pessoas);
        return p ? { nome: p.nome, documento: p.documento ?? null } : row;
      });
    }
  }
  return out;
}
