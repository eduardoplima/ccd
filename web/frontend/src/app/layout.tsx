import type { Metadata } from "next";
import { Roboto } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";

import { Providers } from "./providers";

import "./globals.css";

const roboto = Roboto({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Coordenadoria de Controle de Decisões",
  description: "Webapp da CCD do TCE-RN — módulos CCD, CGAD e FRAP.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  // suppressHydrationWarning: o next-themes escreve a classe do tema no <html>
  // antes da hidratação, e o servidor não tem como saber qual é.
  return (
    <html lang="pt-BR" className={roboto.variable} suppressHydrationWarning>
      <body className="font-sans antialiased">
        <Providers>
          {children}
          {/* dentro do Providers: o Toaster lê o tema pelo next-themes */}
          <Toaster richColors position="top-right" />
        </Providers>
      </body>
    </html>
  );
}
