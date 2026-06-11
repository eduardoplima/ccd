import type { CSSProperties } from "react";

/**
 * Cor determinística (estável) por texto de marcador: o mesmo marcador sempre
 * recebe a mesma cor. Deriva um matiz HSL de um hash da string.
 */
export function marcadorColor(name: string): CSSProperties {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (Math.imul(hash, 31) + name.charCodeAt(i)) | 0;
  }
  const hue = ((hash % 360) + 360) % 360;
  return {
    backgroundColor: `hsl(${hue} 72% 92%)`,
    color: `hsl(${hue} 70% 26%)`,
    borderColor: `hsl(${hue} 55% 78%)`,
  };
}
