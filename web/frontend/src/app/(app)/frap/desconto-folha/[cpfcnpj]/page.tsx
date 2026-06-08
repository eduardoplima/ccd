import { PessoaDetail } from "./_pessoa-detail";

export default async function Page({ params }: { params: Promise<{ cpfcnpj: string }> }) {
  const { cpfcnpj } = await params;
  return <PessoaDetail cpfCnpj={decodeURIComponent(cpfcnpj)} />;
}
