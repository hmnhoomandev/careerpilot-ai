import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HomePage from "./page";

describe("HomePage", () => {
  it("identifies the page as a development foundation", () => {
    render(<HomePage />);

    expect(
      screen.getByRole("heading", { name: "Repository foundation ready" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/product workflows begin/i)).toBeInTheDocument();
  });
});
