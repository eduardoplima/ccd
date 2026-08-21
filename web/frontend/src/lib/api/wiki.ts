import { z } from "zod";

import { apiClient } from "@/lib/api-client";
import {
  wikiPageMetaSchema,
  wikiPageSchema,
  wikiSearchHitSchema,
  type WikiPage,
  type WikiPageMeta,
  type WikiSearchHit,
} from "@/schemas/wiki";

export async function listWikiPages(): Promise<WikiPageMeta[]> {
  const { data } = await apiClient.get("/api/v1/wiki/pages");
  return z.array(wikiPageMetaSchema).parse(data);
}

export async function getWikiPage(slug: string): Promise<WikiPage> {
  const { data } = await apiClient.get(`/api/v1/wiki/pages/${slug}`);
  return wikiPageSchema.parse(data);
}

export async function saveWikiPage(slug: string, content: string): Promise<WikiPage> {
  const { data } = await apiClient.put(`/api/v1/wiki/pages/${slug}`, { content });
  return wikiPageSchema.parse(data);
}

export async function deleteWikiOverride(slug: string): Promise<void> {
  await apiClient.delete(`/api/v1/wiki/pages/${slug}/override`);
}

export async function searchWiki(q: string): Promise<WikiSearchHit[]> {
  const { data } = await apiClient.get("/api/v1/wiki/search", { params: { q } });
  return z.array(wikiSearchHitSchema).parse(data);
}
