"use client";

import { parseAsString, useQueryState } from "nuqs";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { AntecedentesTab } from "./_antecedentes-tab";
import { DescontoFolhaTab } from "./_desconto-folha-tab";

export default function AutomacaoPage() {
  const [tab, setTab] = useQueryState("tab", parseAsString.withDefault("desconto-folha"));

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Automação</h1>

      <Tabs value={tab} onValueChange={(v) => void setTab(v)}>
        <TabsList>
          <TabsTrigger value="desconto-folha">Desconto em Folha</TabsTrigger>
          <TabsTrigger value="antecedentes">Antecedentes</TabsTrigger>
        </TabsList>

        <TabsContent value="desconto-folha" className="pt-4">
          <DescontoFolhaTab />
        </TabsContent>

        <TabsContent value="antecedentes" className="pt-4">
          <AntecedentesTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
