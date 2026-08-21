"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type ClaimBannerProps = {
  currentUsername: string | null;
  claimedBy: string | null;
  onReclaim: () => void;
  onBack: () => void;
  isReclaiming?: boolean;
};

// ponytail: reserva não expira — é só um aviso de quem está no item; qualquer
// um pode reservar por cima (poucos usuários).
export function ClaimBanner({
  currentUsername,
  claimedBy,
  onReclaim,
  onBack,
  isReclaiming,
}: ClaimBannerProps) {
  const isOwn = !!claimedBy && claimedBy === currentUsername;

  if (!claimedBy) {
    return (
      <div className="flex items-center justify-between rounded-md border bg-muted px-4 py-2 text-sm">
        <span>Item sem reserva. Clique em &ldquo;Reservar&rdquo; para iniciar.</span>
        <Button
          size="sm"
          onClick={onReclaim}
          disabled={isReclaiming}
          data-testid="claim-banner-reclaim"
        >
          {isReclaiming ? "Reservando..." : "Reservar"}
        </Button>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center justify-between rounded-md border px-4 py-2 text-sm",
        isOwn ? "border-emerald-500 bg-emerald-50" : "border-amber-500 bg-amber-50",
      )}
      data-testid="claim-banner"
    >
      <span>{isOwn ? "Reservado por você" : `Reservado por ${claimedBy}`}</span>
      {isOwn ? null : (
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={onBack}>
            Voltar para lista
          </Button>
          <Button
            size="sm"
            onClick={onReclaim}
            disabled={isReclaiming}
            data-testid="claim-banner-reclaim"
          >
            {isReclaiming ? "Reservando..." : "Reservar para mim"}
          </Button>
        </div>
      )}
    </div>
  );
}
