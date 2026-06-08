"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function PeriodPicker({
  startDate,
  endDate,
  onChange,
}: {
  startDate: string;
  endDate: string;
  onChange: (range: { startDate: string; endDate: string }) => void;
}) {
  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="flex flex-col gap-1">
        <Label htmlFor="period-start" className="text-xs">
          De
        </Label>
        <Input
          id="period-start"
          type="date"
          value={startDate}
          max={endDate || undefined}
          onChange={(e) => onChange({ startDate: e.target.value, endDate })}
        />
      </div>
      <div className="flex flex-col gap-1">
        <Label htmlFor="period-end" className="text-xs">
          Até
        </Label>
        <Input
          id="period-end"
          type="date"
          value={endDate}
          min={startDate || undefined}
          onChange={(e) => onChange({ startDate, endDate: e.target.value })}
        />
      </div>
    </div>
  );
}
