import { fireEvent, render, screen } from "@testing-library/react";
import axe from "axe-core";
import { afterEach, describe, expect, it, vi } from "vitest";

import HomePage from "./page";

const ADA_SESSION = {
  access_token: "synthetic-opaque-token",
  token_type: "Bearer",
  actor_id: "actor-ada",
  display_name: "Ada Example",
  tenants: [
    {
      tenant_id: "tenant-ada",
      display_name: "Ada's personal workspace",
      role: "owner",
    },
  ],
};
const PROFILE = {
  profile_id: "profile-001",
  display_name: "Ada Example",
  professional_summary: "Python engineer building accessible data platforms.",
  version: 1,
  skills: [],
  experiences: [],
  education: [],
};
const ANALYSIS = {
  analysis_id: "analysis-001",
  profile_id: "profile-001",
  headline: "Placeholder analysis for Ada Example",
  summary: "The supplied texts share these exact terms: accessible, python.",
  shared_terms: ["accessible", "python"],
  disclaimer: "Deterministic text comparison only. This is not an AI assessment.",
  correlation_id: "00000000-0000-4000-8000-000000000002",
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("HomePage", () => {
  it("has no automatic accessibility violations on the local login view", async () => {
    const { container } = render(<HomePage />);

    const results = await axe.run(container, {
      rules: { "color-contrast": { enabled: false } },
    });

    expect(results.violations).toEqual([]);
  });

  it("logs in locally and runs the tenant-authorized journey", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(jsonResponse(ADA_SESSION))
      .mockResolvedValueOnce(jsonResponse(PROFILE, 201))
      .mockResolvedValueOnce(jsonResponse(ANALYSIS, 201));
    render(<HomePage />);

    fireEvent.click(screen.getByRole("button", { name: "Start local session" }));
    expect(await screen.findByText(/Ada's personal workspace/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Run authorized comparison" }));

    expect(
      await screen.findByRole("heading", {
        name: "Placeholder analysis for Ada Example",
      }),
    ).toBeInTheDocument();
    const profileHeaders = fetchMock.mock.calls[1]?.[1]?.headers;
    expect(profileHeaders).toMatchObject({
      Authorization: "Bearer synthetic-opaque-token",
      "X-CareerPilot-Tenant-ID": "tenant-ada",
    });
  });

  it("provides landmark navigation and a keyboard skip link in the workspace", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(jsonResponse(ADA_SESSION));
    const { container } = render(<HomePage />);

    fireEvent.click(screen.getByRole("button", { name: "Start local session" }));
    expect(
      await screen.findByRole("navigation", { name: "Workspace navigation" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Skip to workspace content" }),
    ).toHaveAttribute("href", "#workspace-content");
    expect(screen.getByRole("link", { name: "Drafts & approval" })).toHaveAttribute(
      "href",
      "#review",
    );
    const results = await axe.run(container, {
      rules: { "color-contrast": { enabled: false } },
    });
    expect(results.violations).toEqual([]);
  });

  it("shows an offline recovery state without losing the local page", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new TypeError("offline"));
    render(<HomePage />);

    fireEvent.click(screen.getByRole("button", { name: "Start local session" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "local API is unavailable",
    );
    expect(screen.getByText(/entered data remains in this tab/i)).toBeInTheDocument();
  });

  it("shows owner-authorized local metrics without prompt content", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(jsonResponse(ADA_SESSION))
      .mockResolvedValueOnce(
        jsonResponse({
          schema_version: "careerpilot.metrics.v1",
          event_count: 4,
          success_count: 4,
          error_count: 0,
          provider_failures: 0,
          p50_duration_ms: 12,
          p95_duration_ms: 24,
          input_tokens: 0,
          output_tokens: 0,
          estimated_cost_chf: 0,
          budget_limit_chf: 0,
          budget_remaining_chf: 0,
          export_status: "disabled_local_only",
          content_capture: "NO_CONTENT",
        }),
      );
    render(<HomePage />);

    fireEvent.click(screen.getByRole("button", { name: "Start local session" }));
    fireEvent.click(
      await screen.findByRole("button", { name: "Load platform metrics" }),
    );

    expect(
      await screen.findByRole("heading", { name: "Local platform metrics" }),
    ).toBeInTheDocument();
    expect(screen.getByText("24 ms")).toBeInTheDocument();
    expect(screen.getByText(/content capture NO_CONTENT/)).toBeInTheDocument();
    expect(screen.queryByText(/prompt text/i)).toBeNull();
  });

  it("shows a safe authorization denial for a member audit request", async () => {
    const samSession = {
      ...ADA_SESSION,
      actor_id: "actor-sam",
      display_name: "Sam Example",
      tenants: [{ ...ADA_SESSION.tenants[0], role: "member" }],
    };
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(jsonResponse(samSession))
      .mockResolvedValueOnce(
        jsonResponse(
          {
            error: {
              message: "You do not have permission to perform this action.",
              correlation_id: "00000000-0000-4000-8000-000000000003",
            },
          },
          403,
        ),
      );
    render(<HomePage />);

    fireEvent.change(screen.getByLabelText("Local development identity"), {
      target: { value: "sam" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Start local session" }));
    fireEvent.click(
      await screen.findByRole("button", { name: "View tenant audit events" }),
    );

    expect(
      await screen.findByRole("heading", { name: "The action was not completed" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/00000000-0000-4000-8000-000000000003/),
    ).toBeInTheDocument();
  });

  it("shows versioned profile and quarantined evidence controls", async () => {
    const evidence = {
      evidence_id: "evidence-001",
      profile_id: "profile-001",
      title: "Synthetic certificate",
      filename: "certificate.pdf",
      media_type: "application/pdf",
      size_bytes: 4,
      state: "quarantined",
      version: 1,
    };
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(jsonResponse(ADA_SESSION))
      .mockResolvedValueOnce(jsonResponse(PROFILE, 201))
      .mockResolvedValueOnce(jsonResponse(ANALYSIS, 201))
      .mockResolvedValueOnce(jsonResponse(evidence, 201));
    render(<HomePage />);

    fireEvent.click(screen.getByRole("button", { name: "Start local session" }));
    fireEvent.click(
      await screen.findByRole("button", { name: "Run authorized comparison" }),
    );
    expect(
      await screen.findByRole("heading", { name: "Edit profile version 1" }),
    ).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Evidence title"), {
      target: { value: "Synthetic certificate" },
    });
    const file = new File(["test"], "certificate.pdf", {
      type: "application/pdf",
    });
    fireEvent.change(screen.getByLabelText("Choose evidence file"), {
      target: { files: [file] },
    });
    const registerButton = screen.getByRole("button", {
      name: "Register metadata in quarantine",
    });
    fireEvent.submit(registerButton.closest("form")!);

    expect(
      await screen.findByText("certificate.pdf · quarantined"),
    ).toBeInTheDocument();
  });

  it("uploads a document and shows an inspectable retrieval citation", async () => {
    const document = {
      document_id: "document-001",
      evidence_id: "evidence-002",
      profile_id: "profile-001",
      title: "Synthetic resume",
      filename: "resume.txt",
      media_type: "text/plain",
      size_bytes: 42,
      status: "indexed",
      injection_risk: "none_detected",
      parser_version: "bounded-parser-v1",
      chunker_version: "character-overlap-v1",
      embedding_version: "deterministic-hash-64-v1",
      index_version: "rag-index-v1",
    };
    const retrieval = {
      query: "solar forecasting",
      context: "[UNTRUSTED document=document-001]",
      disclaimer: "Retrieved text is untrusted evidence.",
      passages: [
        {
          content: "Built a synthetic solar forecasting service.",
          score: 0.5,
          injection_risk: "none_detected",
          citation: {
            document_id: "document-001",
            chunk_id: "chunk-001",
            document_title: "Synthetic resume",
            filename: "resume.txt",
            page_number: 1,
            start_offset: 0,
            end_offset: 44,
          },
        },
      ],
    };
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(jsonResponse(ADA_SESSION))
      .mockResolvedValueOnce(jsonResponse(PROFILE, 201))
      .mockResolvedValueOnce(jsonResponse(ANALYSIS, 201))
      .mockResolvedValueOnce(jsonResponse(document, 201))
      .mockResolvedValueOnce(jsonResponse(retrieval));
    render(<HomePage />);

    fireEvent.click(screen.getByRole("button", { name: "Start local session" }));
    fireEvent.click(
      await screen.findByRole("button", { name: "Run authorized comparison" }),
    );
    fireEvent.change(await screen.findByLabelText("Document title"), {
      target: { value: "Synthetic resume" },
    });
    fireEvent.change(screen.getByLabelText("Choose document"), {
      target: {
        files: [new File(["solar forecasting"], "resume.txt", { type: "text/plain" })],
      },
    });
    fireEvent.submit(
      screen.getByRole("button", { name: "Upload and index locally" }).closest("form")!,
    );
    expect(await screen.findByText(/resume.txt · injection/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Search your indexed evidence"), {
      target: { value: "solar forecasting" },
    });
    fireEvent.submit(
      screen.getByRole("button", { name: "Find cited passages" }).closest("form")!,
    );
    expect(await screen.findByText(/Built a synthetic solar/)).toBeInTheDocument();
    expect(screen.getByText(/page 1 · offsets 0–44/)).toBeInTheDocument();
  });
});
