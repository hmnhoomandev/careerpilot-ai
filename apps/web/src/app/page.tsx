"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import {
  CareerPilotApiError,
  changeLocalRole,
  deleteDocument,
  loadAuditEvents,
  loginLocalUser,
  registerEvidence,
  searchDocuments,
  runDeterministicJourney,
  updateProfile,
  uploadDocument,
} from "../lib/careerpilot-api";
import type {
  AnalysisResult,
  AuditEvent,
  EvidenceItem,
  DocumentRecord,
  LocalSession,
  Profile,
  RetrievalResult,
} from "../lib/careerpilot-api";

export default function HomePage() {
  const [session, setSession] = useState<LocalSession | null>(null);
  const [tenantId, setTenantId] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [retrieval, setRetrieval] = useState<RetrievalResult | null>(null);
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
      const result = await runDeterministicJourney({
        session,
        tenantId,
        displayName: String(data.get("displayName")),
        professionalSummary: String(data.get("professionalSummary")),
        jobDescription: String(data.get("jobDescription")),
      });
      setAnalysis(result.analysis);
      setProfile(result.profile);
    } catch (caught) {
      setError(toApiError(caught));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleProfileUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !tenantId || !profile) return;
    setError(null);
    const data = new FormData(event.currentTarget);
    try {
      const saved = await updateProfile({
        session,
        tenantId,
        profile,
        displayName: String(data.get("profileDisplayName")),
        professionalSummary: String(data.get("profileSummary")),
        skills: String(data.get("skills"))
          .split(",")
          .map((skill) => skill.trim())
          .filter(Boolean),
      });
      setProfile(saved);
      setNotice(`Profile saved as version ${saved.version}.`);
    } catch (caught) {
      setError(toApiError(caught));
    }
  }

  async function handleEvidence(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !tenantId || !profile) return;
    setError(null);
    const form = event.currentTarget;
    const data = new FormData(form);
    const file = data.get("evidenceFile");
    if (!(file instanceof File)) return;
    try {
      const saved = await registerEvidence({
        session,
        tenantId,
        profileId: profile.profile_id,
        title: String(data.get("evidenceTitle")),
        file,
      });
      setEvidence((items) => [...items, saved]);
      setNotice(
        "Evidence metadata registered in quarantine; file bytes were not sent.",
      );
      form.reset();
    } catch (caught) {
      setError(toApiError(caught));
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

  async function handleDocumentUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !tenantId || !profile) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    const file = data.get("documentFile");
    if (!(file instanceof File)) return;
    setError(null);
    try {
      const document = await uploadDocument({
        session,
        tenantId,
        profileId: profile.profile_id,
        title: String(data.get("documentTitle")),
        file,
      });
      setDocuments((items) => [...items, document]);
      setNotice("Document indexed locally. Retrieved text remains untrusted.");
      form.reset();
    } catch (caught) {
      setError(toApiError(caught));
    }
  }

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !tenantId) return;
    const data = new FormData(event.currentTarget);
    setError(null);
    try {
      setRetrieval(
        await searchDocuments({
          session,
          tenantId,
          query: String(data.get("retrievalQuery")),
        }),
      );
    } catch (caught) {
      setError(toApiError(caught));
    }
  }

  async function confirmDelete(documentId: string) {
    if (!session || !tenantId) return;
    if (!window.confirm("Delete this document and all searchable derivatives?")) return;
    try {
      await deleteDocument({ session, tenantId, documentId });
      setDocuments((items) => items.filter((item) => item.document_id !== documentId));
      setRetrieval(null);
      setNotice("Document bytes, chunks, and vectors were deleted.");
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
    setProfile(null);
    setEvidence([]);
    setDocuments([]);
    setRetrieval(null);
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

          {profile ? (
            <section className="panel" aria-labelledby="profile-heading">
              <p className="eyebrow">Persistent profile foundation</p>
              <h2 id="profile-heading">Edit profile version {profile.version}</h2>
              <form onSubmit={handleProfileUpdate}>
                <div className="field">
                  <label htmlFor="profileDisplayName">Display name</label>
                  <input
                    id="profileDisplayName"
                    name="profileDisplayName"
                    minLength={2}
                    maxLength={100}
                    required
                    defaultValue={profile.display_name}
                  />
                </div>
                <div className="field">
                  <label htmlFor="profileSummary">Professional summary</label>
                  <textarea
                    id="profileSummary"
                    name="profileSummary"
                    minLength={20}
                    maxLength={1000}
                    required
                    defaultValue={profile.professional_summary}
                  />
                </div>
                <div className="field">
                  <label htmlFor="skills">Skills</label>
                  <p id="skills-help" className="help">
                    Comma-separated, user-asserted skills.
                  </p>
                  <input
                    id="skills"
                    name="skills"
                    aria-describedby="skills-help"
                    defaultValue={profile.skills.join(", ")}
                  />
                </div>
                <button type="submit">Save profile version</button>
              </form>
            </section>
          ) : null}

          {profile ? (
            <section className="panel" aria-labelledby="retrieval-heading">
              <p className="eyebrow">Phase 5 · local secure retrieval</p>
              <h2 id="retrieval-heading">Index and search documents</h2>
              <p className="help">
                Upload UTF-8 text or text-based PDF files up to 10 MB. Document text is
                treated as untrusted data and results always include source citations.
              </p>
              <form onSubmit={handleDocumentUpload}>
                <div className="field">
                  <label htmlFor="documentTitle">Document title</label>
                  <input
                    id="documentTitle"
                    name="documentTitle"
                    minLength={2}
                    required
                  />
                </div>
                <div className="field">
                  <label htmlFor="documentFile">Choose document</label>
                  <input
                    id="documentFile"
                    name="documentFile"
                    type="file"
                    accept="text/plain,application/pdf"
                    required
                  />
                </div>
                <button type="submit">Upload and index locally</button>
              </form>
              {documents.length ? (
                <ul className="evidence-list">
                  {documents.map((document) => (
                    <li key={document.document_id}>
                      <span>
                        <strong>{document.title}</strong>
                        <br />
                        {document.filename} · injection: {document.injection_risk}
                      </span>
                      <button
                        type="button"
                        className="secondary"
                        onClick={() => confirmDelete(document.document_id)}
                      >
                        Delete
                      </button>
                    </li>
                  ))}
                </ul>
              ) : null}
              <form onSubmit={handleSearch}>
                <div className="field">
                  <label htmlFor="retrievalQuery">Search your indexed evidence</label>
                  <input
                    id="retrievalQuery"
                    name="retrievalQuery"
                    minLength={2}
                    required
                  />
                </div>
                <button type="submit">Find cited passages</button>
              </form>
              {retrieval ? <RetrievalPanel result={retrieval} /> : null}
            </section>
          ) : null}

          {profile ? (
            <section className="panel" aria-labelledby="evidence-heading">
              <p className="eyebrow">Metadata-only security preview</p>
              <h2 id="evidence-heading">Register evidence</h2>
              <p className="help">
                PDF, JPEG, or PNG up to 10 MB. Phase 4 sends metadata only; every item
                stays quarantined until a future scanner marks it clean.
              </p>
              <form onSubmit={handleEvidence}>
                <div className="field">
                  <label htmlFor="evidenceTitle">Evidence title</label>
                  <input
                    id="evidenceTitle"
                    name="evidenceTitle"
                    minLength={2}
                    required
                  />
                </div>
                <div className="field">
                  <label htmlFor="evidenceFile">Choose evidence file</label>
                  <input
                    id="evidenceFile"
                    name="evidenceFile"
                    type="file"
                    accept="application/pdf,image/jpeg,image/png"
                    required
                  />
                </div>
                <button type="submit">Register metadata in quarantine</button>
              </form>
              {evidence.length ? (
                <ul className="evidence-list">
                  {evidence.map((item) => (
                    <li key={item.evidence_id}>
                      <strong>{item.title}</strong>
                      <span>
                        {item.filename} · {item.state}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : null}
            </section>
          ) : null}

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

function RetrievalPanel({ result }: { result: RetrievalResult }) {
  return (
    <div className="retrieval-results" aria-live="polite">
      <h3>Retrieved passages</h3>
      {result.passages.length === 0 ? <p>No supporting passage was found.</p> : null}
      {result.passages.map((passage) => (
        <blockquote key={passage.citation.chunk_id}>
          <p>{passage.content}</p>
          <cite>
            {passage.citation.document_title} · {passage.citation.filename} · page{" "}
            {passage.citation.page_number} · offsets {passage.citation.start_offset}–
            {passage.citation.end_offset} · injection: {passage.injection_risk}
          </cite>
        </blockquote>
      ))}
      <p className="disclaimer">{result.disclaimer}</p>
    </div>
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
