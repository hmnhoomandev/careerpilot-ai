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

export type DocumentRecord = {
  document_id: string;
  evidence_id: string;
  profile_id: string;
  title: string;
  filename: string;
  media_type: string;
  size_bytes: number;
  status: string;
  injection_risk: string;
  parser_version: string;
  chunker_version: string;
  embedding_version: string;
  index_version: string;
};

export type RetrievalResult = {
  query: string;
  context: string;
  disclaimer: string;
  passages: Array<{
    content: string;
    score: number;
    injection_risk: string;
    citation: {
      document_id: string;
      chunk_id: string;
      document_title: string;
      filename: string;
      page_number: number;
      start_offset: number;
      end_offset: number;
    };
  }>;
};

export type A2UIMessage = {
  schema: "careerpilot.a2ui.v1";
  component: "editable_career_draft" | "approval_review";
  actions: Array<"edit" | "approve" | "reject" | "request_more_information" | "cancel">;
  data: Record<string, unknown>;
};

export type CareerDraft = {
  draft_id: string;
  version: number;
  kind: "resume" | "cover_letter";
  title: string;
  sections: string[];
  claims: Array<{
    claim_id: string;
    text: string;
    status: string;
    citations: Array<{
      document_id: string;
      chunk_id: string;
      filename: string;
      page_number: number;
      start_offset: number;
      end_offset: number;
    }>;
  }>;
  content_hash: string;
  pii_flags: string[];
  policy_flags: string[];
  approval_id: string;
  approval_status: string;
  approval_revision: number;
  correlation_id: string;
  messages: A2UIMessage[];
};

export type NotificationItem = {
  notification_id: string;
  event_id: string;
  category: "application" | "follow_up" | "approval";
  subject_ref: string;
  message_key: string;
  created_at: string;
  read_at: string | null;
};

export type PlatformMetrics = {
  schema_version: "careerpilot.metrics.v1";
  event_count: number;
  success_count: number;
  error_count: number;
  provider_failures: number;
  p50_duration_ms: number;
  p95_duration_ms: number;
  input_tokens: number;
  output_tokens: number;
  estimated_cost_chf: number;
  budget_limit_chf: number;
  budget_remaining_chf: number;
  export_status: string;
  content_capture: "NO_CONTENT";
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

export async function uploadDocument(input: {
  session: LocalSession;
  tenantId: string;
  profileId: string;
  title: string;
  file: File;
}): Promise<DocumentRecord> {
  const body = new FormData();
  body.set("profile_id", input.profileId);
  body.set("title", input.title);
  body.set("file", input.file);
  const headers = authenticatedHeaders(input.session, input.tenantId);
  delete headers["Content-Type"];
  const response = await fetch(`${API_BASE_URL}/api/v1/documents`, {
    method: "POST",
    headers,
    body,
  });
  return parseResponse<DocumentRecord>(response);
}

export async function searchDocuments(input: {
  session: LocalSession;
  tenantId: string;
  query: string;
}): Promise<RetrievalResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/retrieval/search`, {
    method: "POST",
    headers: authenticatedHeaders(input.session, input.tenantId),
    body: JSON.stringify({ query: input.query, limit: 5 }),
  });
  return parseResponse<RetrievalResult>(response);
}

export async function deleteDocument(input: {
  session: LocalSession;
  tenantId: string;
  documentId: string;
}): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/documents/${input.documentId}/deletion`,
    {
      method: "POST",
      headers: authenticatedHeaders(input.session, input.tenantId),
      body: JSON.stringify({ confirmed: true }),
    },
  );
  if (!response.ok) await parseResponse(response);
}

export async function createCareerDraft(input: {
  session: LocalSession;
  tenantId: string;
  profileId: string;
  kind: "resume" | "cover_letter";
  jobDescription: string;
}): Promise<CareerDraft> {
  const response = await fetch(`${API_BASE_URL}/api/v1/drafts`, {
    method: "POST",
    headers: authenticatedHeaders(input.session, input.tenantId),
    body: JSON.stringify({
      profile_id: input.profileId,
      kind: input.kind,
      job_description: input.jobDescription,
    }),
  });
  return parseResponse<CareerDraft>(response);
}

export async function decideCareerDraft(input: {
  session: LocalSession;
  tenantId: string;
  draft: CareerDraft;
  decision: "approve" | "reject" | "request_more_information" | "cancel";
  feedback?: string;
}): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/approvals/${input.draft.approval_id}/decisions`,
    {
      method: "POST",
      headers: authenticatedHeaders(input.session, input.tenantId),
      body: JSON.stringify({
        decision: input.decision,
        expected_revision: input.draft.approval_revision,
        expected_draft_version: input.draft.version,
        expected_draft_hash: input.draft.content_hash,
        feedback: input.feedback || null,
      }),
    },
  );
  await parseResponse(response);
}

export async function loadNotifications(
  session: LocalSession,
  tenantId: string,
): Promise<NotificationItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/notifications`, {
    headers: authenticatedHeaders(session, tenantId),
  });
  return parseResponse<NotificationItem[]>(response);
}

export async function saveNotificationPreferences(
  session: LocalSession,
  tenantId: string,
  enabledCategories: NotificationItem["category"][],
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/notification-preferences`, {
    method: "PUT",
    headers: authenticatedHeaders(session, tenantId),
    body: JSON.stringify({ enabled_categories: enabledCategories }),
  });
  await parseResponse(response);
}

export async function loadPlatformMetrics(
  session: LocalSession,
  tenantId: string,
): Promise<PlatformMetrics> {
  const response = await fetch(`${API_BASE_URL}/api/v1/platform/metrics`, {
    headers: authenticatedHeaders(session, tenantId),
  });
  return parseResponse<PlatformMetrics>(response);
}
