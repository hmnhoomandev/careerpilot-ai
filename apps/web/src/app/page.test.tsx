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
});
