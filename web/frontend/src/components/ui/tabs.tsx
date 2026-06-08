"use client";

import * as React from "react";
import { Tabs as RTabs } from "radix-ui";

import { cn } from "@/lib/utils";

const Tabs = RTabs.Root;

const TabsList = React.forwardRef<
  React.ElementRef<typeof RTabs.List>,
  React.ComponentPropsWithoutRef<typeof RTabs.List>
>(({ className, ...props }, ref) => (
  <RTabs.List
    ref={ref}
    data-slot="tabs-list"
    data-variant="line"
    className={cn(
      "inline-flex h-10 items-center justify-start gap-6 border-b border-border",
      className,
    )}
    {...props}
  />
));
TabsList.displayName = "TabsList";

const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof RTabs.Trigger>,
  React.ComponentPropsWithoutRef<typeof RTabs.Trigger>
>(({ className, ...props }, ref) => (
  <RTabs.Trigger
    ref={ref}
    data-slot="tabs-trigger"
    className={cn(
      "relative inline-flex h-10 items-center justify-center px-1 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none data-[state=active]:text-foreground data-[state=active]:after:absolute data-[state=active]:after:bottom-[-1px] data-[state=active]:after:left-0 data-[state=active]:after:right-0 data-[state=active]:after:h-[2px]",
      className,
    )}
    {...props}
  />
));
TabsTrigger.displayName = "TabsTrigger";

const TabsContent = React.forwardRef<
  React.ElementRef<typeof RTabs.Content>,
  React.ComponentPropsWithoutRef<typeof RTabs.Content>
>(({ className, ...props }, ref) => (
  <RTabs.Content
    ref={ref}
    className={cn("mt-4 focus-visible:outline-none", className)}
    {...props}
  />
));
TabsContent.displayName = "TabsContent";

export { Tabs, TabsContent, TabsList, TabsTrigger };
