export type AnalysisResult = {
  analysis_id: string;
  profile_id: string;
  headline: string;
  summary: string;
  shared_terms: string[];
  disclaimer: string;
  correlation_id: string;
};

type ProfileResponse = {
  profile_id: string;
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
  displayName: string;
  professionalSummary: string;
  jobDescription: string;
}): Promise<AnalysisResult> {
  const profileResponse = await fetch(`${API_BASE_URL}/api/v1/profiles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      display_name: input.displayName,
      professional_summary: input.professionalSummary,
    }),
  });
  const profile = await parseResponse<ProfileResponse>(profileResponse);

  const analysisResponse = await fetch(`${API_BASE_URL}/api/v1/analyses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      profile_id: profile.profile_id,
      job_description: input.jobDescription,
    }),
  });
  return parseResponse<AnalysisResult>(analysisResponse);
}
