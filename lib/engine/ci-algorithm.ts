import type { CiContext, CiStatus } from "@/lib/engine/status";

export type CiPhase = "signal" | "attention" | "threshold" | "alignment" | "action" | "seal" | "return";
export type CiPolarity = "+" | "=" | "-";

export type CiAlgorithmResult = {
  algorithmVersion: "ci-core-v1";
  context: CiContext;
  lockedMinute: number;
  phase: CiPhase;
  polarity: CiPolarity;
  resonanceScore: number;
  status: CiStatus;
  signalLabel: string;
  artifactSeed: string;
  explanationKey: string;
};

const CONTEXT_WEIGHT: Record<CiContext, number> = {
  career: 11,
  love: 17,
  timing: 23,
};

const PHASES: CiPhase[] = ["signal", "attention", "threshold", "alignment", "action", "seal", "return"];

function positiveModulo(value: number, modulo: number): number {
  return ((value % modulo) + modulo) % modulo;
}

function mapScoreToStatus(score: number): CiStatus {
  if (score <= 34) return "NOT_NOW";
  if (score <= 66) return "HOLD";
  return "PROCEED";
}

function mapStatusToPolarity(status: CiStatus): CiPolarity {
  if (status === "PROCEED") return "+";
  if (status === "HOLD") return "=";
  return "-";
}

function getSignalLabel(status: CiStatus, phase: CiPhase): string {
  if (status === "PROCEED") return `Open ${phase}`;
  if (status === "HOLD") return `Align ${phase}`;
  return `Close ${phase}`;
}

export function calculateCiMoment(input: { context: CiContext; lockedMinute: number }): CiAlgorithmResult {
  const contextWeight = CONTEXT_WEIGHT[input.context];
  const phaseIndex = positiveModulo(input.lockedMinute + contextWeight, PHASES.length);
  const phase = PHASES[phaseIndex];

  const raw = (input.lockedMinute * contextWeight + phaseIndex * 31 + contextWeight * 7) % 101;
  const resonanceScore = positiveModulo(raw, 101);
  const status = mapScoreToStatus(resonanceScore);
  const polarity = mapStatusToPolarity(status);

  return {
    algorithmVersion: "ci-core-v1",
    context: input.context,
    lockedMinute: input.lockedMinute,
    phase,
    polarity,
    resonanceScore,
    status,
    signalLabel: getSignalLabel(status, phase),
    artifactSeed: `ci-${input.lockedMinute}-${input.context}-${resonanceScore}`,
    explanationKey: `${status.toLowerCase()}_${phase}`,
  };
}
