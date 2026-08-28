import { OrgaoDetail } from "./_orgao-detail";

export default async function Page({ params }: { params: Promise<{ idOrgao: string }> }) {
  const { idOrgao } = await params;
  const parsed = Number.parseInt(idOrgao, 10);
  return <OrgaoDetail idOrgao={Number.isFinite(parsed) ? parsed : 0} />;
}
