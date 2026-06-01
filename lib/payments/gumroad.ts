const DEFAULT_GUMROAD_URL = "https://cimoment.gumroad.com/l/rwffi";

export type CheckoutInput = {
  artifactId: string;
  verifyHash: string;
  sessionId: string;
  source?: string;
  utmSource?: string;
  utmMedium?: string;
  utmCampaign?: string;
};

export function getGumroadBaseUrl(): string {
  return process.env.NEXT_PUBLIC_GUMROAD_URL || DEFAULT_GUMROAD_URL;
}

export function buildCheckoutUrl(input: CheckoutInput): string {
  const url = new URL(getGumroadBaseUrl());
  const passthrough = JSON.stringify({
    artifactId: input.artifactId,
    verifyHash: input.verifyHash,
    sessionId: input.sessionId,
    source: input.source,
    utmSource: input.utmSource,
    utmMedium: input.utmMedium,
    utmCampaign: input.utmCampaign,
  });

  url.searchParams.set("wanted", "true");
  url.searchParams.set("passthrough", passthrough);
  url.searchParams.set("verify_hash", input.verifyHash);
  url.searchParams.set("artifact_id", input.artifactId);
  url.searchParams.set("session_id", input.sessionId);

  if (input.utmSource) url.searchParams.set("utm_source", input.utmSource);
  if (input.utmMedium) url.searchParams.set("utm_medium", input.utmMedium);
  if (input.utmCampaign) url.searchParams.set("utm_campaign", input.utmCampaign);

  return url.toString();
}
