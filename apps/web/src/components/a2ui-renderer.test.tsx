import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { A2UIRenderer } from "./a2ui-renderer";

describe("A2UIRenderer", () => {
  it("renders only allowlisted components and actions as inert text", () => {
    const action = vi.fn();
    render(
      <A2UIRenderer
        messages={[
          {
            schema: "careerpilot.a2ui.v1",
            component: "editable_career_draft",
            actions: ["edit"],
            data: {
              title: "Evidence-grounded resume",
              sections: ["<img src=x onerror=alert(1)>"],
            },
          },
        ]}
        onAction={action}
      />,
    );

    expect(screen.getByText("<img src=x onerror=alert(1)>")).toBeInTheDocument();
    expect(document.querySelector("img")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "edit" }));
    expect(action).toHaveBeenCalledWith("edit");
  });

  it("fails closed for unknown schemas, components, and actions", () => {
    render(
      <A2UIRenderer
        messages={[
          {
            schema: "attacker.v1",
            component: "script",
            actions: ["submit_application"],
            data: { html: "<script>alert(1)</script>" },
          },
        ]}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Unsupported presentation content was safely blocked.",
    );
    expect(screen.queryByRole("button")).toBeNull();
  });
});
