"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const [montado, setMontado] = useState(false);

  // O tema só é conhecido no cliente; renderizar o ícone antes disso dá
  // divergência de hidratação.
  useEffect(() => setMontado(true), []);

  const escuro = resolvedTheme === "dark";

  return (
    <Button
      variant="outline"
      size="sm"
      className="border-white/40 bg-transparent text-white hover:bg-white/10"
      onClick={() => setTheme(escuro ? "light" : "dark")}
      title={escuro ? "Modo claro" : "Modo noturno"}
      aria-label={escuro ? "Mudar para o modo claro" : "Mudar para o modo noturno"}
    >
      {montado && escuro ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </Button>
  );
}
