"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";

const PARAM = "min_conf";

/**
 * URL-backed confidence filter. The URL carries a 0–100 percentage
 * (``?min_conf=95``); the backend takes a 0–1 fraction. Keeping it in the
 * URL makes the filter survive navigation between list/detail/unmapped and
 * lets reviewers share a link to a filtered view.
 */
export function useMinConfidence() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const raw = searchParams.get(PARAM);
  const percentage = (() => {
    if (raw == null) return 0;
    const n = Number(raw);
    if (!Number.isFinite(n)) return 0;
    return Math.max(0, Math.min(100, Math.round(n)));
  })();

  const fraction = percentage / 100;

  const setPercentage = useCallback(
    (value: number) => {
      const clamped = Math.max(0, Math.min(100, Math.round(value)));
      const sp = new URLSearchParams(searchParams.toString());
      if (clamped <= 0) {
        sp.delete(PARAM);
      } else {
        sp.set(PARAM, String(clamped));
      }
      // Reset the page param too — confidence change rebases pagination.
      sp.delete("page");
      const qs = sp.toString();
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    },
    [pathname, router, searchParams],
  );

  return { percentage, fraction, setPercentage };
}
