"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// href relativo ao diretório da página atual → rota /wiki/<slug>
function resolveHref(href: string, baseSlug: string): string | null {
  if (/^[a-z][a-z0-9+.-]*:/i.test(href) || href.startsWith("#") || href.startsWith("/")) {
    return null;
  }
  const parts = baseSlug.split("/").slice(0, -1);
  for (const seg of href.replace(/\.md$/, "").split("/")) {
    if (!seg || seg === ".") continue;
    if (seg === "..") parts.pop();
    else parts.push(seg);
  }
  return `/wiki/${parts.join("/")}`;
}

export function WikiMarkdown({ content, baseSlug }: { content: string; baseSlug: string }) {
  return (
    <div className="prose prose-neutral dark:prose-invert max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children }) => {
            const internal = href ? resolveHref(href, baseSlug) : null;
            if (internal) return <Link href={internal}>{children}</Link>;
            return (
              <a href={href} target="_blank" rel="noreferrer">
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
