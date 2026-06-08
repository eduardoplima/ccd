import type { Metadata } from "next";
import { Roboto } from "next/font/google";
import { Toaster } from "sonner";

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
  return (
    <html lang="pt-BR" className={roboto.variable}>
      <body className="font-sans antialiased">
        <Providers>{children}</Providers>
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
