"use client";

import * as React from "react";
import { Checkbox as RCheckbox } from "radix-ui";
import { Check, Minus } from "lucide-react";

import { cn } from "@/lib/utils";

const Checkbox = React.forwardRef<
  React.ElementRef<typeof RCheckbox.Root>,
  React.ComponentPropsWithoutRef<typeof RCheckbox.Root>
>(({ className, ...props }, ref) => (
  <RCheckbox.Root
    ref={ref}
    className={cn(
      "peer size-4 shrink-0 rounded-sm border border-input bg-background ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground data-[state=indeterminate]:bg-primary data-[state=indeterminate]:text-primary-foreground",
      className,
    )}
    {...props}
  >
    <RCheckbox.Indicator className="flex items-center justify-center text-current">
      {props.checked === "indeterminate" ? (
        <Minus className="size-3.5" />
      ) : (
        <Check className="size-3.5" />
      )}
    </RCheckbox.Indicator>
  </RCheckbox.Root>
));
Checkbox.displayName = "Checkbox";

export { Checkbox };
