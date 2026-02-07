/**
 * ci-Artifact-System — Deterministic Engine
 * Minute-based signal generation bound to a time phase.
 */

export type CiContext = 'career' | 'love' | 'timing';
export type CiStatus = 'PROCEED' | 'HOLD' | 'NOT_NOW';

const SALT: Record<CiContext, number> = { career: 1, love: 2, timing: 3 };
const STATES: CiStatus[] = ['PROCEED', 'HOLD', 'NOT_NOW'];

export function getCiStatus(context: CiContext, lockedMinuteUtc: number): CiStatus {
  const seed = Number(lockedMinuteUtc) + (SALT[context] ?? 0);
  return STATES[((seed % 3) + 3) % 3]; // Handles negative mod
}

export function formatStatus(status: CiStatus): string {
  return status === 'NOT_NOW' ? 'NOT NOW' : status;
}
