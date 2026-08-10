import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import axe from "axe-core";
import { afterEach, describe, expect, it, vi } from "vitest";

import HomePage from "./page";

const PROFILE = { profile_id: "profile-001" };
const ANALYSIS = {
  analysis_id: "analysis-001",
  profile_id: "profile-001",
  headline: "Placeholder analysis for Ada Example",
  summary: "The supplied texts share these exact terms: accessible, python.",
  shared_terms: ["accessible", "python"],
  disclaimer: "Deterministic text comparison only. This is not an AI assessment.",
  correlation_id: "00000000-0000-4000-8000-000000000002",
};

function jsonResponse(body: unknown, status = 201): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("HomePage", () => {
  it("has no automatic accessibility violations in its initial state", async () => {
    const { container } = render(<HomePage />);

    const results = await axe.run(container, {
      rules: { "color-contrast": { enabled: false } },
    });

    expect(results.violations).toEqual([]);
  });

  it("crosses the UI client contract and renders the deterministic result", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(jsonResponse(PROFILE))
      .mockResolvedValueOnce(jsonResponse(ANALYSIS));
    render(<HomePage />);

    fireEvent.click(
      screen.getByRole("button", { name: "Run deterministic comparison" }),
    );

    expect(
      await screen.findByRole("heading", {
        name: "Placeholder analysis for Ada Example",
      }),
    ).toBeInTheDocument();
    expect(screen.getByText("accessible")).toBeInTheDocument();
    expect(
      screen.getByText(/00000000-0000-4000-8000-000000000002/),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls[0]?.[0]).toBe("http://127.0.0.1:8000/api/v1/profiles");
  });

  it("shows a safe API error and its correlation ID", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      jsonResponse(
        {
          error: {
            message: "Please correct the highlighted fields and try again.",
            correlation_id: "00000000-0000-4000-8000-000000000003",
          },
        },
        422,
      ),
    );
    render(<HomePage />);

    fireEvent.click(
      screen.getByRole("button", { name: "Run deterministic comparison" }),
    );

    await waitFor(() => {
      expect(
        screen.getByRole("heading", {
          name: "We could not complete the comparison",
        }),
      ).toBeInTheDocument();
    });
    expect(
      screen.getByText(/00000000-0000-4000-8000-000000000003/),
    ).toBeInTheDocument();
  });
});
