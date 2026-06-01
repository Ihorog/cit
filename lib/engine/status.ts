export type CiContext = "career" | "love" | "timing";

export type CiStatus = "PROCEED" | "HOLD" | "NOT_NOW";

export const CI_CONTEXTS: { id: CiContext; label: string; description: string }[] = [
  { id: "career", label: "Career", description: "Work, direction, execution." },
  { id: "love", label: "Love", description: "Relation, contact, resonance." },
  { id: "timing", label: "Timing", description: "Moment, rhythm, transition." },
];

const STATUS_ORDER: CiStatus[] = ["PROCEED", "HOLD", "NOT_NOW"];

const CONTEXT_INDEX: Record<CiContext, number> = {
  career: 1,
  love: 2,
  timing: 3,
};

export function getLockedMinute(date = new Date()): number {
  return Math.floor(date.getTime() / 60_000);
}

export function calculateStatus(context: CiContext, lockedMinute = getLockedMinute()): CiStatus {
  const index = (lockedMinute + CONTEXT_INDEX[context]) % STATUS_ORDER.length;
  return STATUS_ORDER[index];
}

export function getStatusCopy(status: CiStatus): string {
  switch (status) {
    case "PROCEED":
      return "The signal is open. Move with attention, not impulse.";
    case "HOLD":
      return "The signal asks for alignment. Pause before committing.";
    case "NOT_NOW":
      return "The signal is closed for now. Let the moment pass.";
  }
}
