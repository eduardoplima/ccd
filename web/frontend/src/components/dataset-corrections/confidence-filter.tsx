"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useMinConfidence } from "@/hooks/use-min-confidence";

const PRESETS = [0, 50, 80, 95, 99];

export function ConfidenceFilter() {
  const { percentage, setPercentage } = useMinConfidence();

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-md border bg-white p-3">
      <label
        htmlFor="min-confidence"
        className="text-sm font-medium text-muted-foreground"
      >
        Confiança mínima
      </label>
      <div className="flex items-center gap-1">
        <Input
          id="min-confidence"
          type="number"
          min={0}
          max={100}
          step={1}
          value={percentage}
          onChange={(e) => setPercentage(Number(e.target.value))}
          className="w-20"
        />
        <span className="text-sm text-muted-foreground">%</span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        step={1}
        value={percentage}
        onChange={(e) => setPercentage(Number(e.target.value))}
        className="h-2 flex-1 min-w-[8rem] cursor-pointer appearance-none rounded-full bg-muted accent-emerald-500"
      />
      <div className="flex gap-1">
        {PRESETS.map((p) => (
          <Button
            key={p}
            type="button"
            variant={p === percentage ? "default" : "outline"}
            size="sm"
            onClick={() => setPercentage(p)}
          >
            {p === 0 ? "Tudo" : `≥${p}%`}
          </Button>
        ))}
      </div>
    </div>
  );
}
