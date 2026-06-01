export type CiEventName =
  | "page_view"
  | "context_selected"
  | "threshold_confirmed"
  | "result_rendered"
  | "seal_clicked"
  | "gumroad_checkout_opened"
  | "gumroad_order_matched"
  | "artifact_verified"
  | "repeat_visit_30d"
  | "membership_started"
  | "membership_renewed"
  | "membership_canceled";

export type CiTelemetryEvent = {
  eventName: CiEventName;
  sessionId: string;
  anonymousUserId?: string;
  source?: string;
  utmSource?: string;
  utmMedium?: string;
  utmCampaign?: string;
  referrer?: string;
  route?: string;
  context?: string;
  artifactId?: string;
  verifyHash?: string;
  checkoutId?: string;
  orderId?: string;
  membershipId?: string;
  deviceType?: string;
  timestamp: string;
};

export function createSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `session_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

export function trackEvent(event: Omit<CiTelemetryEvent, "timestamp">): CiTelemetryEvent {
  const payload: CiTelemetryEvent = {
    ...event,
    timestamp: new Date().toISOString(),
  };

  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("ci:telemetry", { detail: payload }));
    console.info("[ci telemetry]", payload);
  }

  return payload;
}
