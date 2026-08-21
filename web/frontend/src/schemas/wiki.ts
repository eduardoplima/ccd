import { z } from "zod";

// mirrors backend WikiPageMeta
export const wikiPageMetaSchema = z.object({
  slug: z.string(),
  title: z.string(),
  editado: z.boolean(),
});
export type WikiPageMeta = z.infer<typeof wikiPageMetaSchema>;

// mirrors backend WikiPage
export const wikiPageSchema = wikiPageMetaSchema.extend({
  content: z.string(),
});
export type WikiPage = z.infer<typeof wikiPageSchema>;

// mirrors backend WikiSearchHit
export const wikiSearchHitSchema = z.object({
  slug: z.string(),
  title: z.string(),
  snippet: z.string(),
});
export type WikiSearchHit = z.infer<typeof wikiSearchHitSchema>;
