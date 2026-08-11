"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import {
  CareerPilotApiError,
  changeLocalRole,
  loadAuditEvents,
  loginLocalUser,
  runDeterministicJourney,
} from "../lib/careerpilot-api";
import type { AnalysisResult, AuditEvent, LocalSession } from "../lib/careerpilot-api";

export default function HomePage() {
  const [session, setSession] = useState<LocalSession | null>(null);
  const [tenantId, setTenantId] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState<CareerPilotApiError | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const data = new FormData(event.currentTarget);
    try {
      const localSession = await loginLocalUser(String(data.get("localUserId")));
      setSession(localSession);
      setTenantId(localSession.tenants[0]?.tenant_id ?? "");
      setNotice(`Signed in locally as ${localSession.display_name}.`);
    } catch (caught) {
      setError(toApiError(caught));
    }
  }

  async function handleJourney(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !tenantId) return;
    setAnalysis(null);
    setError(null);
    setSubmitting(true);
    const data = new FormData(event.currentTarget);
    try {
      setAnalysis(
        await runDeterministicJourney({
          session,
          tenantId,
          displayName: String(data.get("displayName")),
          professionalSummary: String(data.get("professionalSummary")),
          jobDescription: String(data.get("jobDescription")),
        }),
      );
    } catch (caught) {
      setError(toApiError(caught));
    } finally {
      setSubmitting(false);
    }
  }

  async function showAudit() {
    if (!session || !tenantId) return;
    setError(null);
    try {
      setAuditEvents(await loadAuditEvents(session, tenantId));
    } catch (caught) {
      setError(toApiError(caught));
    }
  }

  async function promoteSam() {
    if (!session || !tenantId) return;
    setError(null);
    try {
      await changeLocalRole(session, tenantId, "actor-sam", "owner");
      setNotice("Sam now has the local owner role in Ada's workspace.");
    } catch (caught) {
      setError(toApiError(caught));
    }
  }

  function signOut() {
    setSession(null);
    setTenantId("");
    setAnalysis(null);
    setAuditEvents([]);
    setNotice("Local session cleared from this browser tab.");
  }

  const activeTenant = session?.tenants.find((tenant) => tenant.tenant_id === tenantId);

  return (
    <main>
      <header className="hero">
        <p className="eyebrow">CareerPilot AI · Local security preview</p>
        <h1>Explore an isolated personal workspace</h1>
        <p className="lede">
          Synthetic users and sessions only. This development adapter is not a
          production login and stores nothing after the API restarts.
        </p>
      </header>

      {!session ? (
        <section className="panel" aria-labelledby="login-heading">
          <h2 id="login-heading">Choose a synthetic user</h2>
          <form onSubmit={handleLogin} className="compact-form">
            <div className="field">
              <label htmlFor="localUserId">Local development identity</label>
              <select id="localUserId" name="localUserId" defaultValue="ada">
                <option value="ada">Ada — owner of Ada workspace</option>
                <option value="grace">Grace — owner of Grace workspace</option>
                <option value="sam">Sam — member of Ada workspace</option>
              </select>
            </div>
            <button type="submit">Start local session</button>
          </form>
        </section>
      ) : (
        <>
          <section className="session-bar" aria-label="Current local session">
            <div>
              <strong>{session.display_name}</strong>
              <span>
                {activeTenant?.display_name} · role: {activeTenant?.role}
              </span>
            </div>
            <button type="button" className="secondary" onClick={signOut}>
              Clear local session
            </button>
          </section>

          <section className="panel" aria-labelledby="journey-heading">
            <h2 id="journey-heading">Authorized profile comparison</h2>
            <form onSubmit={handleJourney}>
              <div className="field">
                <label htmlFor="displayName">Display name</label>
                <input
                  id="displayName"
                  name="displayName"
                  minLength={2}
                  maxLength={100}
                  required
                  defaultValue={session.display_name}
                />
              </div>
              <div className="field">
                <label htmlFor="professionalSummary">Professional summary</label>
                <p id="summary-help" className="help">
                  Synthetic data only; 20–1,000 characters.
                </p>
                <textarea
                  id="professionalSummary"
                  name="professionalSummary"
                  aria-describedby="summary-help"
                  minLength={20}
                  maxLength={1000}
                  required
                  defaultValue="Python engineer building accessible and reliable data platforms."
                />
              </div>
              <div className="field">
                <label htmlFor="jobDescription">Job description</label>
                <p id="job-help" className="help">
                  Use a synthetic or explicitly permitted source; 50–5,000 characters.
                </p>
                <textarea
                  id="jobDescription"
                  name="jobDescription"
                  aria-describedby="job-help"
                  minLength={50}
                  maxLength={5000}
                  required
                  defaultValue="We seek a Python engineer to build accessible services for a reliable data platform and collaborative team."
                />
              </div>
              <button type="submit" disabled={submitting}>
                {submitting ? "Comparing…" : "Run authorized comparison"}
              </button>
            </form>
          </section>

          <section className="panel" aria-labelledby="security-heading">
            <h2 id="security-heading">Security controls</h2>
            <p className="help">
              Audit viewing and role changes require owner permission. Sam initially has
              the member role.
            </p>
            <div className="actions">
              <button type="button" className="secondary" onClick={showAudit}>
                View tenant audit events
              </button>
              {session.actor_id === "actor-ada" ? (
                <button type="button" className="secondary" onClick={promoteSam}>
                  Promote Sam to owner
                </button>
              ) : null}
            </div>
          </section>
        </>
      )}

      <div aria-live="polite" aria-atomic="true">
        {notice ? <p className="notice">{notice}</p> : null}
        {error ? (
          <section className="panel error" aria-labelledby="error-heading">
            <h2 id="error-heading">The action was not completed</h2>
            <p>{error.message}</p>
            {error.correlationId ? (
              <p className="meta">Correlation ID: {error.correlationId}</p>
            ) : null}
          </section>
        ) : null}
        {analysis ? <AnalysisPanel analysis={analysis} /> : null}
        {auditEvents.length > 0 ? <AuditPanel events={auditEvents} /> : null}
      </div>
    </main>
  );
}

function AnalysisPanel({ analysis }: { analysis: AnalysisResult }) {
  return (
    <section className="panel result" aria-labelledby="result-heading">
      <p className="eyebrow">Authorized deterministic result</p>
      <h2 id="result-heading">{analysis.headline}</h2>
      <p>{analysis.summary}</p>
      <ul className="terms">
        {analysis.shared_terms.map((term) => (
          <li key={term}>{term}</li>
        ))}
      </ul>
      <p className="disclaimer">{analysis.disclaimer}</p>
      <p className="meta">Correlation ID: {analysis.correlation_id}</p>
    </section>
  );
}

function AuditPanel({ events }: { events: AuditEvent[] }) {
  return (
    <section className="panel" aria-labelledby="audit-heading">
      <h2 id="audit-heading">Tenant audit events</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Outcome</th>
              <th>Action</th>
              <th>Actor</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.event_id}>
                <td>{event.outcome}</td>
                <td>{event.action}</td>
                <td>{event.actor_id}</td>
                <td>{event.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function toApiError(caught: unknown): CareerPilotApiError {
  return caught instanceof CareerPilotApiError
    ? caught
    : new CareerPilotApiError("The local API is unavailable. Please try again.");
}
