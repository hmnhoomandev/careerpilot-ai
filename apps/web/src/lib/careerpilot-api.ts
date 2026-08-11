export type AnalysisResult = {
  analysis_id: string;
  profile_id: string;
  headline: string;
  summary: string;
  shared_terms: string[];
  disclaimer: string;
  correlation_id: string;
};

export type TenantSummary = {
  tenant_id: string;
  display_name: string;
  role: string;
};

export type LocalSession = {
  access_token: string;
  token_type: "Bearer";
  actor_id: string;
  display_name: string;
  tenants: TenantSummary[];
};

export type AuditEvent = {
  event_id: string;
  occurred_at: string;
  actor_id: string;
  action: string;
  outcome: string;
  reason: string;
  correlation_id: string;
};

export type Profile = {
  profile_id: string;
  display_name: string;
  professional_summary: string;
  version: number;
  skills: string[];
  experiences: Array<{
    title: string;
    organization: string;
    start_date: string;
    end_date: string | null;
    description: string;
  }>;
  education: Array<{
    institution: string;
    qualification: string;
    start_date: string | null;
    end_date: string | null;
  }>;
};

export type EvidenceItem = {
  evidence_id: string;
  profile_id: string;
  title: string;
  filename: string;
  media_type: string;
  size_bytes: number;
  state: string;
  version: number;
};

type ErrorResponse = {
  error?: {
    message?: string;
    correlation_id?: string;
  };
};

export class CareerPilotApiError extends Error {
  constructor(
    message: string,
    readonly correlationId?: string,
  ) {
    super(message);
    this.name = "CareerPilotApiError";
  }
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_CAREERPILOT_API_URL ?? "http://127.0.0.1:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  const body = (await response.json()) as T | ErrorResponse;
  if (!response.ok) {
    const error = body as ErrorResponse;
    throw new CareerPilotApiError(
      error.error?.message ?? "The local API could not complete the request.",
      error.error?.correlation_id ??
        response.headers.get("X-Correlation-ID") ??
        undefined,
    );
  }
  return body as T;
}

export async function runDeterministicJourney(input: {
  session: LocalSession;
  tenantId: string;
  displayName: string;
  professionalSummary: string;
  jobDescription: string;
}): Promise<{ analysis: AnalysisResult; profile: Profile }> {
  const profileResponse = await fetch(`${API_BASE_URL}/api/v1/profiles`, {
    method: "POST",
    headers: authenticatedHeaders(input.session, input.tenantId),
    body: JSON.stringify({
      display_name: input.displayName,
      professional_summary: input.professionalSummary,
    }),
  });
  const profile = await parseResponse<Profile>(profileResponse);

  const analysisResponse = await fetch(`${API_BASE_URL}/api/v1/analyses`, {
    method: "POST",
    headers: authenticatedHeaders(input.session, input.tenantId),
    body: JSON.stringify({
      profile_id: profile.profile_id,
      job_description: input.jobDescription,
    }),
  });
  return {
    analysis: await parseResponse<AnalysisResult>(analysisResponse),
    profile,
  };
}

function authenticatedHeaders(
  session: LocalSession,
  tenantId: string,
): Record<string, string> {
  return {
    Authorization: `Bearer ${session.access_token}`,
    "Content-Type": "application/json",
    "X-CareerPilot-Tenant-ID": tenantId,
  };
}

export async function loginLocalUser(localUserId: string): Promise<LocalSession> {
  const response = await fetch(`${API_BASE_URL}/api/v1/dev/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ local_user_id: localUserId }),
  });
  return parseResponse<LocalSession>(response);
}

export async function loadAuditEvents(
  session: LocalSession,
  tenantId: string,
): Promise<AuditEvent[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/audit-events`, {
    headers: authenticatedHeaders(session, tenantId),
  });
  return parseResponse<AuditEvent[]>(response);
}

export async function changeLocalRole(
  session: LocalSession,
  tenantId: string,
  actorId: string,
  role: "owner" | "member",
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/memberships/${actorId}`, {
    method: "PATCH",
    headers: authenticatedHeaders(session, tenantId),
    body: JSON.stringify({ role }),
  });
  await parseResponse(response);
}

export async function updateProfile(input: {
  session: LocalSession;
  tenantId: string;
  profile: Profile;
  displayName: string;
  professionalSummary: string;
  skills: string[];
}): Promise<Profile> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/profiles/${input.profile.profile_id}`,
    {
      method: "PATCH",
      headers: authenticatedHeaders(input.session, input.tenantId),
      body: JSON.stringify({
        display_name: input.displayName,
        professional_summary: input.professionalSummary,
        skills: input.skills,
        experiences: input.profile.experiences,
        education: input.profile.education,
        expected_version: input.profile.version,
      }),
    },
  );
  return parseResponse<Profile>(response);
}

export async function registerEvidence(input: {
  session: LocalSession;
  tenantId: string;
  profileId: string;
  title: string;
  file: File;
}): Promise<EvidenceItem> {
  const response = await fetch(`${API_BASE_URL}/api/v1/evidence`, {
    method: "POST",
    headers: authenticatedHeaders(input.session, input.tenantId),
    body: JSON.stringify({
      profile_id: input.profileId,
      title: input.title,
      filename: input.file.name,
      media_type: input.file.type || "application/octet-stream",
      size_bytes: input.file.size,
    }),
  });
  return parseResponse<EvidenceItem>(response);
}
