"use client";

import type { ReactNode } from "react";

import type { A2UIMessage } from "../lib/careerpilot-api";

const ALLOWED_ACTIONS = new Set([
  "edit",
  "approve",
  "reject",
  "request_more_information",
  "cancel",
]);

type A2UIRendererProps = {
  messages: unknown[];
  onAction?: (action: string) => void;
};

/** Render a closed set of presentation messages without interpreting HTML or URLs. */
export function A2UIRenderer({ messages, onAction }: A2UIRendererProps) {
  return (
    <div className="a2ui-stack" aria-label="Structured review components">
      {messages.map((message, index) => {
        const validated = validateMessage(message);
        return validated ? (
          <A2UIComponent
            key={`${validated.component}-${index}`}
            message={validated}
            onAction={onAction}
          />
        ) : (
          <div className="state-card denied" role="alert" key={`rejected-${index}`}>
            Unsupported presentation content was safely blocked.
          </div>
        );
      })}
    </div>
  );
}

function A2UIComponent({
  message,
  onAction,
}: {
  message: A2UIMessage;
  onAction?: (action: string) => void;
}) {
  if (message.component === "editable_career_draft") {
    const title = textValue(message.data.title, "Career draft");
    const sections = stringList(message.data.sections);
    return (
      <article className="structured-card">
        <p className="eyebrow">Evidence-controlled draft</p>
        <h3>{title}</h3>
        {sections.map((section, index) => (
          <p key={`${index}-${section}`}>{section}</p>
        ))}
        <SafeActions actions={message.actions} onAction={onAction} />
      </article>
    );
  }
  const status = textValue(message.data.status, "pending");
  return (
    <article className="structured-card approval-card">
      <p className="eyebrow">Human decision required</p>
      <h3>Approval review</h3>
      <p>
        <span className={`status-pill ${status}`}>{status.replaceAll("_", " ")}</span>
      </p>
      <p className="help">
        Actions are submitted to the server with the exact draft version and hash.
      </p>
      <SafeActions actions={message.actions} onAction={onAction} />
    </article>
  );
}

function SafeActions({
  actions,
  onAction,
}: {
  actions: string[];
  onAction?: (action: string) => void;
}) {
  return (
    <div className="actions">
      {actions
        .filter((action) => ALLOWED_ACTIONS.has(action))
        .map((action) => (
          <button
            key={action}
            type="button"
            className={action === "approve" ? "" : "secondary"}
            onClick={() => onAction?.(action)}
          >
            {action.replaceAll("_", " ")}
          </button>
        ))}
    </div>
  );
}

function validateMessage(value: unknown): A2UIMessage | null {
  if (!value || typeof value !== "object") return null;
  const candidate = value as Record<string, unknown>;
  if (candidate.schema !== "careerpilot.a2ui.v1") return null;
  if (
    candidate.component !== "editable_career_draft" &&
    candidate.component !== "approval_review"
  )
    return null;
  if (
    !Array.isArray(candidate.actions) ||
    !candidate.actions.every(
      (item) => typeof item === "string" && ALLOWED_ACTIONS.has(item),
    )
  )
    return null;
  if (
    !candidate.data ||
    typeof candidate.data !== "object" ||
    Array.isArray(candidate.data)
  )
    return null;
  return candidate as A2UIMessage;
}

function textValue(value: unknown, fallback: string): string {
  return typeof value === "string" ? value.slice(0, 500) : fallback;
}

function stringList(value: unknown): ReactNode[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === "string").slice(0, 20);
}
