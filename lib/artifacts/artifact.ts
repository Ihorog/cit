import type { CiContext, CiStatus } from "@/lib/engine/status";

export type CiArtifact = {
  artifactId: string;
  artifactCode: string;
  verifyHash: string;
  context: CiContext;
  status: CiStatus;
  lockedMinute: number;
  createdAt: string;
};

function randomSegment(length: number): string {
  const alphabet = "0123456789abcdef";
  let output = "";
  const values = new Uint8Array(length);

  if (typeof crypto !== "undefined" && crypto.getRandomValues) {
    crypto.getRandomValues(values);
    for (const value of values) output += alphabet[value % alphabet.length];
    return output;
  }

  for (let index = 0; index < length; index += 1) {
    output += alphabet[Math.floor(Math.random() * alphabet.length)];
  }

  return output;
}

export function createArtifact(input: {
  context: CiContext;
  status: CiStatus;
  lockedMinute: number;
  date?: Date;
}): CiArtifact {
  const createdAt = (input.date ?? new Date()).toISOString();
  const artifactId = `art_${randomSegment(16)}`;
  const artifactCode = `ci-${randomSegment(2)}-${randomSegment(5)}`;
  const verifyHash = randomSegment(16);

  return {
    artifactId,
    artifactCode,
    verifyHash,
    context: input.context,
    status: input.status,
    lockedMinute: input.lockedMinute,
    createdAt,
  };
}
