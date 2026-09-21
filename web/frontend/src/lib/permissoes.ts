// mirrors backend app/permissoes.py (MODULOS + pode)
type Permissoes = { papel: string; permissoes: { modulo: string; editar: boolean }[] };

export const MODULOS = [
  { key: "ccd.inicio", grupo: "ccd", label: "Início", href: "/ccd" },
  {
    key: "ccd.desconto-folha",
    grupo: "ccd",
    label: "Desconto em Folha",
    href: "/ccd/desconto-folha",
  },
  { key: "ccd.beneficios", grupo: "ccd", label: "Benefícios", href: "/ccd/beneficios" },
  { key: "ccd.automacao", grupo: "ccd", label: "Automação", href: "/ccd/automacao" },
  { key: "ccd.alertas", grupo: "ccd", label: "Alertas", href: "/ccd/alertas" },
  { key: "cgad.reviews", grupo: "cgad", label: "Revisões", href: "/cgad/reviews" },
  { key: "cgad.etl", grupo: "cgad", label: "Extrações", href: "/cgad/etl" },
  { key: "cgad.dashboards", grupo: "cgad", label: "Painéis", href: "/cgad/dashboards" },
  { key: "cgad.dataset", grupo: "cgad", label: "Conjunto de Dados", href: "/cgad/dataset" },
  { key: "frap.extratos", grupo: "frap", label: "Extratos", href: "/frap/extratos" },
  { key: "frap.jobs", grupo: "frap", label: "Extrações", href: "/frap/jobs" },
  { key: "wiki", grupo: "wiki", label: "Wiki", href: "/wiki" },
] as const;

export type Modulo = (typeof MODULOS)[number]["key"];

// Rotas fora do menu herdam o módulo de quem as usa.
const PREFIXOS_EXTRAS: [string, Modulo][] = [
  ["/ccd/siai-pessoal", "ccd.desconto-folha"],
  ["/frap/busca", "frap.extratos"],
  ["/cgad/admin", "cgad.dataset"],
];

export function podeVer(me: Permissoes | undefined, modulo: Modulo): boolean {
  if (!me) return false;
  if (me.papel !== "restrito") return true;
  return me.permissoes.some((p) => p.modulo === modulo);
}

export function podeEditar(me: Permissoes | undefined, modulo: Modulo): boolean {
  if (!me) return false;
  if (me.papel === "admin") return true;
  return me.permissoes.some((p) => p.modulo === modulo && p.editar);
}

/** Módulo dono da rota (prefixo mais longo); `null` para rotas livres (/conta, /admin). */
export function moduloDaRota(pathname: string): Modulo | null {
  const candidatos: [string, Modulo][] = [
    ...PREFIXOS_EXTRAS,
    ...MODULOS.map((m): [string, Modulo] => [m.href, m.key]),
  ];
  return (
    candidatos
      .filter(([href]) => pathname === href || pathname.startsWith(href + "/"))
      .sort((a, b) => b[0].length - a[0].length)[0]?.[1] ?? null
  );
}

export function primeiraRotaVisivel(me: Permissoes): string {
  return MODULOS.find((m) => podeVer(me, m.key))?.href ?? "/conta";
}
