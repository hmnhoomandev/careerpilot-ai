"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { A2UIRenderer } from "../components/a2ui-renderer";
import {
  CareerPilotApiError,
  changeLocalRole,
  createCareerDraft,
  decideCareerDraft,
  deleteDocument,
  loadAuditEvents,
  loadNotifications,
  loginLocalUser,
  registerEvidence,
  runDeterministicJourney,
  saveNotificationPreferences,
  searchDocuments,
  updateProfile,
  uploadDocument,
} from "../lib/careerpilot-api";
import type {
  AnalysisResult,
  AuditEvent,
  CareerDraft,
  DocumentRecord,
  EvidenceItem,
  LocalSession,
  NotificationItem,
  Profile,
  RetrievalResult,
} from "../lib/careerpilot-api";

const NAVIGATION = [
  ["overview", "Overview"],
  ["profile", "Profile & evidence"],
  ["job", "Job workspace"],
  ["review", "Drafts & approval"],
  ["interview", "Interview prep"],
  ["applications", "Applications"],
  ["settings", "Settings & audit"],
] as const;

export default function HomePage() {
  const [session, setSession] = useState<LocalSession | null>(null);
  const [tenantId, setTenantId] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [retrieval, setRetrieval] = useState<RetrievalResult | null>(null);
  const [draft, setDraft] = useState<CareerDraft | null>(null);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState<CareerPilotApiError | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const activeTenant = session?.tenants.find((item) => item.tenant_id === tenantId);

  async function run(action: string, operation: () => Promise<void>) {
    setError(null);
    setBusy(action);
    try {
      await operation();
    } catch (caught) {
      setError(toApiError(caught));
    } finally {
      setBusy(null);
    }
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    await run("login", async () => {
      const result = await loginLocalUser(String(data.get("localUserId")));
      setSession(result);
      setTenantId(result.tenants[0]?.tenant_id ?? "");
      setNotice(`Signed in locally as ${result.display_name}.`);
    });
  }

  async function handleJourney(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !tenantId) return;
    const data = new FormData(event.currentTarget);
    const job = String(data.get("jobDescription"));
    setAnalysis(null);
    await run("journey", async () => {
      const result = await runDeterministicJourney({
        session,
        tenantId,
        displayName: String(data.get("displayName")),
        professionalSummary: String(data.get("professionalSummary")),
        jobDescription: job,
      });
      setAnalysis(result.analysis);
      setProfile(result.profile);
      setJobDescription(job);
      setNotice("Job comparison completed. Review the evidence and limitations below.");
    });
  }

  async function handleProfileUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !tenantId || !profile) return;
    const data = new FormData(event.currentTarget);
    await run("profile", async () => {
      const saved = await updateProfile({
        session,
        tenantId,
        profile,
        displayName: String(data.get("profileDisplayName")),
        professionalSummary: String(data.get("profileSummary")),
        skills: String(data.get("skills"))
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
      });
      setProfile(saved);
      setNotice(`Profile saved as version ${saved.version}.`);
    });
  }

  async function handleEvidence(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !tenantId || !profile) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    const file = data.get("evidenceFile");
    if (!(file instanceof File)) return;
    await run("evidence", async () => {
      const saved = await registerEvidence({
        session,
        tenantId,
        profileId: profile.profile_id,
        title: String(data.get("evidenceTitle")),
        file,
      });
      setEvidence((items) => [...items, saved]);
      form.reset();
      setNotice(
        "Evidence metadata registered in quarantine; file bytes were not sent.",
      );
    });
  }

  async function handleDocumentUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !tenantId || !profile) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    const file = data.get("documentFile");
    if (!(file instanceof File)) return;
    await run("document", async () => {
      const saved = await uploadDocument({
        session,
        tenantId,
        profileId: profile.profile_id,
        title: String(data.get("documentTitle")),
        file,
      });
      setDocuments((items) => [...items, saved]);
      form.reset();
      setNotice("Document indexed locally. Retrieved text remains untrusted.");
    });
  }

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !tenantId) return;
    const query = String(new FormData(event.currentTarget).get("retrievalQuery"));
    await run("search", async () =>
      setRetrieval(await searchDocuments({ session, tenantId, query })),
    );
  }

  async function handleDraft(kind: "resume" | "cover_letter") {
    if (!session || !tenantId || !profile || !jobDescription) return;
    await run("draft", async () => {
      setDraft(
        await createCareerDraft({
          session,
          tenantId,
          profileId: profile.profile_id,
          kind,
          jobDescription,
        }),
      );
      setNotice(
        "A truthful draft is ready for human review. No external action occurred.",
      );
    });
  }

  async function handleDraftAction(action: string) {
    if (
      !session ||
      !tenantId ||
      !draft ||
      !["approve", "reject", "request_more_information", "cancel"].includes(action)
    )
      return;
    const decision = action as
      "approve" | "reject" | "request_more_information" | "cancel";
    if (
      ["approve", "cancel"].includes(decision) &&
      !window.confirm(
        `${decision === "approve" ? "Approve" : "Cancel"} this exact draft version?`,
      )
    )
      return;
    await run("decision", async () => {
      await decideCareerDraft({
        session,
        tenantId,
        draft,
        decision,
        feedback:
          decision === "approve"
            ? undefined
            : "Reviewed in the local Phase 14 workspace.",
      });
      setDraft({
        ...draft,
        approval_status: decision === "approve" ? "approved" : decision,
      });
      setNotice(`Draft decision recorded: ${decision.replaceAll("_", " ")}.`);
    });
  }

  async function confirmDelete(documentId: string) {
    if (
      !session ||
      !tenantId ||
      !window.confirm("Delete this document and all searchable derivatives?")
    )
      return;
    await run("delete", async () => {
      await deleteDocument({ session, tenantId, documentId });
      setDocuments((items) => items.filter((item) => item.document_id !== documentId));
      setRetrieval(null);
      setNotice("Document bytes, chunks, and vectors were deleted.");
    });
  }

  function signOut() {
    setSession(null);
    setTenantId("");
    setProfile(null);
    setAnalysis(null);
    setEvidence([]);
    setDocuments([]);
    setRetrieval(null);
    setDraft(null);
    setNotifications([]);
    setAuditEvents([]);
  }

  if (!session)
    return <LoginView onLogin={handleLogin} busy={busy === "login"} error={error} />;

  return (
    <div className="app-shell">
      <a className="skip-link" href="#workspace-content">
        Skip to workspace content
      </a>
      <aside className="sidebar">
        <Brand />
        <nav aria-label="Workspace navigation">
          <ul>
            {NAVIGATION.map(([id, label]) => (
              <li key={id}>
                <a href={`#${id}`}>{label}</a>
              </li>
            ))}
          </ul>
        </nav>
        <div className="privacy-note">
          <strong>Local & synthetic</strong>
          <span>No production login or external send.</span>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Personal workspace</p>
            <strong>{activeTenant?.display_name}</strong>
          </div>
          <div className="topbar-actions">
            <button
              className="icon-button"
              type="button"
              aria-label="Load notifications"
              onClick={() =>
                run("notifications", async () =>
                  setNotifications(await loadNotifications(session, tenantId)),
                )
              }
            >
              🔔
              <span className="notification-count">
                {notifications.filter((item) => !item.read_at).length}
              </span>
            </button>
            <div className="avatar" aria-hidden="true">
              {session.display_name[0]}
            </div>
            <button type="button" className="text-button" onClick={signOut}>
              Sign out
            </button>
          </div>
        </header>
        <main id="workspace-content" tabIndex={-1}>
          <section id="overview" className="page-heading">
            <div>
              <p className="eyebrow">
                Good to see you, {session.display_name.split(" ")[0]}
              </p>
              <h1>Build your next move on evidence.</h1>
              <p>
                One calm workspace for your profile, target role, truthful documents and
                decisions.
              </p>
            </div>
            <span className="status-pill protected">
              Protected workspace · {activeTenant?.role}
            </span>
          </section>
          <div className="status-region" aria-live="polite" aria-atomic="true">
            {busy ? (
              <div className="state-card loading" role="status">
                <span className="spinner" aria-hidden="true" />
                Working on {busy}…
              </div>
            ) : null}
            {notice ? <p className="notice">{notice}</p> : null}
            {error ? <ErrorState error={error} /> : null}
          </div>
          <section className="metric-grid" aria-label="Journey summary">
            <Metric
              value={
                profile ? `${Math.min(100, 35 + profile.skills.length * 10)}%` : "0%"
              }
              label="Profile readiness"
              tone="green"
            />
            <Metric
              value={analysis ? `${analysis.shared_terms.length}` : "—"}
              label="Supported matches"
              tone="blue"
            />
            <Metric
              value={draft?.approval_status ?? "Not started"}
              label="Review status"
              tone="amber"
            />
            <Metric
              value={`${documents.length}`}
              label="Indexed sources"
              tone="violet"
            />
          </section>
          <section id="job" className="content-grid">
            <article className="panel span-2">
              <SectionTitle
                eyebrow="Target role"
                title="Job workspace"
                subtitle="Use synthetic or explicitly permitted job information."
              />
              <JourneyForm
                session={session}
                onSubmit={handleJourney}
                busy={busy === "journey"}
              />
            </article>
            <article className="panel">
              <SectionTitle
                eyebrow="Workflow"
                title="Agent activity"
                subtitle="Status summaries only—never hidden reasoning."
              />
              <Timeline active={Boolean(analysis)} />
              <button type="button" className="secondary full-width" disabled>
                Cancel active workflow
              </button>
            </article>
          </section>
          {analysis ? (
            <AnalysisPanel analysis={analysis} />
          ) : (
            <EmptyState
              title="No job analysis yet"
              body="Add a target role to see supported matches, gaps and evidence."
            />
          )}
          <section id="profile" className="content-grid">
            <article className="panel">
              <SectionTitle
                eyebrow="Verified foundation"
                title={
                  profile
                    ? `Edit profile version ${profile.version}`
                    : "Professional profile"
                }
                subtitle="Only user-confirmed facts belong here."
              />
              {profile ? (
                <ProfileForm
                  profile={profile}
                  onSubmit={handleProfileUpdate}
                  busy={busy === "profile"}
                />
              ) : (
                <p className="empty-copy">
                  Complete the job workspace to create your local profile.
                </p>
              )}
            </article>
            <article className="panel">
              <SectionTitle
                eyebrow="Evidence library"
                title="Sources & documents"
                subtitle="Uploads are bounded and retrieved text stays untrusted."
              />
              {profile ? (
                <EvidenceForms
                  onEvidence={handleEvidence}
                  onDocument={handleDocumentUpload}
                />
              ) : (
                <p className="empty-copy">Create a profile before adding evidence.</p>
              )}
              <AssetList
                evidence={evidence}
                documents={documents}
                onDelete={confirmDelete}
              />
            </article>
          </section>
          <section className="panel">
            <SectionTitle
              eyebrow="Citations"
              title="Find supporting passages"
              subtitle="Every result keeps its document and location."
            />
            {profile ? (
              <SearchForm onSubmit={handleSearch} busy={busy === "search"} />
            ) : null}
            {retrieval ? (
              <RetrievalPanel result={retrieval} />
            ) : (
              <p className="empty-copy">No cited passages loaded.</p>
            )}
          </section>
          <section id="review" className="panel">
            <SectionTitle
              eyebrow="Truthful documents"
              title="Drafts & approval"
              subtitle="Unsupported claims stay blocked; a human controls every decision."
            />
            <div className="actions">
              <button
                type="button"
                disabled={!analysis || busy === "draft"}
                onClick={() => handleDraft("resume")}
              >
                Create truthful resume
              </button>
              <button
                type="button"
                className="secondary"
                disabled={!analysis || busy === "draft"}
                onClick={() => handleDraft("cover_letter")}
              >
                Create cover letter
              </button>
            </div>
            {draft ? (
              <A2UIRenderer messages={draft.messages} onAction={handleDraftAction} />
            ) : (
              <p className="empty-copy">
                Complete a job comparison before generating a cited draft.
              </p>
            )}
          </section>
          <section id="interview" className="content-grid">
            <article className="panel">
              <SectionTitle
                eyebrow="Practice"
                title="Interview preparation"
                subtitle="A bounded synthetic coaching space."
              />
              <div className="state-card partial">
                <strong>Specialist available as a local lab</strong>
                <span>
                  Live voice and external models are off. No fallback will occur.
                </span>
              </div>
              <button className="secondary" type="button" disabled>
                Start interview lab (not connected)
              </button>
            </article>
            <article id="applications" className="panel">
              <SectionTitle
                eyebrow="After approval"
                title="Application tracker"
                subtitle="Tracking is visible; submission remains manual."
              />
              <div className="application-row">
                <span className="company-mark">N</span>
                <div>
                  <strong>Northstar Analytics</strong>
                  <span>Product Engineer · synthetic fixture</span>
                </div>
                <span className="status-pill draft">Draft</span>
              </div>
              <p className="help">
                Automatic submission and email sending are not enabled.
              </p>
            </article>
          </section>
          <section id="settings" className="content-grid">
            <article className="panel">
              <SectionTitle
                eyebrow="Preferences"
                title="Notifications"
                subtitle="Choose which in-app updates appear."
              />
              <NotificationSettings
                notifications={notifications}
                onSave={(categories) =>
                  run("preferences", () =>
                    saveNotificationPreferences(session, tenantId, categories),
                  )
                }
              />
              <button
                className="secondary"
                type="button"
                onClick={() =>
                  run("notifications", async () =>
                    setNotifications(await loadNotifications(session, tenantId)),
                  )
                }
              >
                Refresh notification inbox
              </button>
              <NotificationList items={notifications} />
            </article>
            <article className="panel">
              <SectionTitle
                eyebrow="Security evidence"
                title="Audit & access"
                subtitle="Tenant-scoped decisions and safe correlation metadata."
              />
              <div className="actions">
                <button
                  type="button"
                  className="secondary"
                  onClick={() =>
                    run("audit", async () =>
                      setAuditEvents(await loadAuditEvents(session, tenantId)),
                    )
                  }
                >
                  View tenant audit events
                </button>
                {session.actor_id === "actor-ada" ? (
                  <button
                    type="button"
                    className="secondary"
                    onClick={() =>
                      run("role", async () => {
                        await changeLocalRole(session, tenantId, "actor-sam", "owner");
                        setNotice(
                          "Sam now has the local owner role in Ada's workspace.",
                        );
                      })
                    }
                  >
                    Promote Sam to owner
                  </button>
                ) : null}
              </div>
              {auditEvents.length ? (
                <AuditPanel events={auditEvents} />
              ) : (
                <p className="empty-copy">
                  Audit events are loaded only when requested.
                </p>
              )}
            </article>
          </section>
        </main>
      </div>
    </div>
  );
}

function Brand() {
  return (
    <div className="brand">
      <span className="brand-mark" aria-hidden="true">
        CP
      </span>
      <div>
        <strong>CareerPilot</strong>
        <span>Evidence first</span>
      </div>
    </div>
  );
}
function LoginView({
  onLogin,
  busy,
  error,
}: {
  onLogin: (event: FormEvent<HTMLFormElement>) => void;
  busy: boolean;
  error: CareerPilotApiError | null;
}) {
  return (
    <main className="login-page">
      <section className="login-story">
        <p className="eyebrow">CareerPilot AI</p>
        <h1>Your career story, grounded in evidence.</h1>
        <p>
          Turn verified experience into focused applications without invented claims or
          automatic submissions.
        </p>
        <ul>
          <li>Evidence-linked matching</li>
          <li>Human-controlled drafts</li>
          <li>Private, tenant-isolated workspace</li>
        </ul>
      </section>
      <section className="login-card" aria-labelledby="login-heading">
        <Brand />
        <h2 id="login-heading">Open the local workspace</h2>
        <p className="help">
          Synthetic identities only. This is not production authentication.
        </p>
        <form onSubmit={onLogin}>
          <div className="field">
            <label htmlFor="localUserId">Local development identity</label>
            <select id="localUserId" name="localUserId" defaultValue="ada">
              <option value="ada">Ada — owner of Ada workspace</option>
              <option value="grace">Grace — owner of Grace workspace</option>
              <option value="sam">Sam — member of Ada workspace</option>
            </select>
          </div>
          <button type="submit" disabled={busy}>
            {busy ? "Opening…" : "Start local session"}
          </button>
        </form>
        {error ? <ErrorState error={error} /> : null}
      </section>
    </main>
  );
}
function SectionTitle({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
}) {
  return (
    <header className="section-title">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <p>{subtitle}</p>
    </header>
  );
}
function Metric({
  value,
  label,
  tone,
}: {
  value: string;
  label: string;
  tone: string;
}) {
  return (
    <article className={`metric ${tone}`}>
      <strong>{value}</strong>
      <span>{label}</span>
    </article>
  );
}
function JourneyForm({
  session,
  onSubmit,
  busy,
}: {
  session: LocalSession;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  busy: boolean;
}) {
  return (
    <form onSubmit={onSubmit}>
      <div className="two-fields">
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
          <textarea
            id="professionalSummary"
            name="professionalSummary"
            minLength={20}
            maxLength={1000}
            required
            defaultValue="Python engineer building accessible and reliable data platforms."
          />
        </div>
      </div>
      <div className="field">
        <label htmlFor="jobDescription">Job description</label>
        <p id="job-help" className="help">
          Synthetic or permitted source; 50–5,000 characters.
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
      <button type="submit" disabled={busy}>
        {busy ? "Comparing…" : "Run authorized comparison"}
      </button>
    </form>
  );
}
function ProfileForm({
  profile,
  onSubmit,
  busy,
}: {
  profile: Profile;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  busy: boolean;
}) {
  return (
    <form onSubmit={onSubmit}>
      <div className="field">
        <label htmlFor="profileDisplayName">Display name</label>
        <input
          id="profileDisplayName"
          name="profileDisplayName"
          required
          minLength={2}
          defaultValue={profile.display_name}
        />
      </div>
      <div className="field">
        <label htmlFor="profileSummary">Professional summary</label>
        <textarea
          id="profileSummary"
          name="profileSummary"
          required
          minLength={20}
          defaultValue={profile.professional_summary}
        />
      </div>
      <div className="field">
        <label htmlFor="skills">Skills</label>
        <input
          id="skills"
          name="skills"
          aria-describedby="skills-help"
          defaultValue={profile.skills.join(", ")}
        />
        <p id="skills-help" className="help">
          Comma-separated, user-confirmed skills.
        </p>
      </div>
      <button type="submit" disabled={busy}>
        Save profile version
      </button>
    </form>
  );
}
function EvidenceForms({
  onEvidence,
  onDocument,
}: {
  onEvidence: (event: FormEvent<HTMLFormElement>) => void;
  onDocument: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="form-stack">
      <form onSubmit={onDocument}>
        <div className="field">
          <label htmlFor="documentTitle">Document title</label>
          <input id="documentTitle" name="documentTitle" minLength={2} required />
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
      <details>
        <summary>Register metadata-only evidence</summary>
        <form onSubmit={onEvidence}>
          <div className="field">
            <label htmlFor="evidenceTitle">Evidence title</label>
            <input id="evidenceTitle" name="evidenceTitle" minLength={2} required />
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
      </details>
    </div>
  );
}
function AssetList({
  evidence,
  documents,
  onDelete,
}: {
  evidence: EvidenceItem[];
  documents: DocumentRecord[];
  onDelete: (id: string) => void;
}) {
  if (!evidence.length && !documents.length)
    return <p className="empty-copy">No evidence added yet.</p>;
  return (
    <ul className="evidence-list">
      {documents.map((item) => (
        <li key={item.document_id}>
          <span>
            <strong>{item.title}</strong>
            <br />
            {item.filename} · injection: {item.injection_risk}
          </span>
          <button
            type="button"
            className="secondary compact"
            onClick={() => onDelete(item.document_id)}
          >
            Delete
          </button>
        </li>
      ))}
      {evidence.map((item) => (
        <li key={item.evidence_id}>
          <span>
            <strong>{item.title}</strong>
            <br />
            {item.filename} · {item.state}
          </span>
        </li>
      ))}
    </ul>
  );
}
function SearchForm({
  onSubmit,
  busy,
}: {
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  busy: boolean;
}) {
  return (
    <form className="inline-form" onSubmit={onSubmit}>
      <div className="field">
        <label htmlFor="retrievalQuery">Search your indexed evidence</label>
        <input id="retrievalQuery" name="retrievalQuery" minLength={2} required />
      </div>
      <button type="submit" disabled={busy}>
        Find cited passages
      </button>
    </form>
  );
}
function Timeline({ active }: { active: boolean }) {
  return (
    <ol className="timeline">
      {[
        "Intake & policy",
        "Job analysis",
        "Evidence retrieval",
        "Match & gaps",
        "Explanation",
      ].map((step, index) => (
        <li className={active ? "complete" : index === 0 ? "current" : ""} key={step}>
          <span aria-hidden="true">{active ? "✓" : index + 1}</span>
          <div>
            <strong>{step}</strong>
            <small>{active ? "Completed" : index === 0 ? "Ready" : "Waiting"}</small>
          </div>
        </li>
      ))}
    </ol>
  );
}
function AnalysisPanel({ analysis }: { analysis: AnalysisResult }) {
  return (
    <section className="panel result" aria-labelledby="result-heading">
      <div className="result-header">
        <div>
          <p className="eyebrow">Evidence-grounded result</p>
          <h2 id="result-heading">{analysis.headline}</h2>
        </div>
        <span className="status-pill protected">Review sources</span>
      </div>
      <p>{analysis.summary}</p>
      <div className="split-result">
        <div>
          <h3>Supported matches</h3>
          <ul className="terms">
            {analysis.shared_terms.map((term) => (
              <li key={term}>{term}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>Skill gaps</h3>
          <p className="empty-copy">
            No unsupported qualification is inferred. Add evidence to resolve unknowns.
          </p>
        </div>
      </div>
      <p className="disclaimer">{analysis.disclaimer}</p>
      <p className="meta">Correlation ID: {analysis.correlation_id}</p>
    </section>
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
function NotificationSettings({
  notifications,
  onSave,
}: {
  notifications: NotificationItem[];
  onSave: (categories: NotificationItem["category"][]) => void;
}) {
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const data = new FormData(event.currentTarget);
        onSave(
          ["application", "approval", "follow_up"].filter((item) =>
            data.has(item),
          ) as NotificationItem["category"][],
        );
      }}
    >
      <fieldset>
        {[
          ["application", "Applications"],
          ["approval", "Approvals"],
          ["follow_up", "Follow-ups"],
        ].map(([value, label]) => (
          <label className="check-row" key={value}>
            <input type="checkbox" name={value} defaultChecked />
            {label}
          </label>
        ))}
      </fieldset>
      <button type="submit" className="secondary">
        Save preferences
      </button>
      <p className="help">{notifications.length} notification(s) currently loaded.</p>
    </form>
  );
}
function NotificationList({ items }: { items: NotificationItem[] }) {
  if (!items.length)
    return <p className="empty-copy">Your in-app notification inbox is empty.</p>;
  return (
    <ul className="notification-list">
      {items.map((item) => (
        <li key={item.notification_id}>
          <span className="status-dot" aria-hidden="true" />
          <div>
            <strong>{item.category.replaceAll("_", " ")}</strong>
            <span>
              {item.message_key} · {item.subject_ref}
            </span>
          </div>
        </li>
      ))}
    </ul>
  );
}
function AuditPanel({ events }: { events: AuditEvent[] }) {
  return (
    <div className="table-wrap">
      <table>
        <caption className="sr-only">Tenant audit events</caption>
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
  );
}
function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <section className="panel empty-state">
      <span aria-hidden="true">◎</span>
      <div>
        <h2>{title}</h2>
        <p>{body}</p>
      </div>
    </section>
  );
}
function ErrorState({ error }: { error: CareerPilotApiError }) {
  return (
    <section className="state-card denied" role="alert" aria-labelledby="error-heading">
      <h2 id="error-heading">The action was not completed</h2>
      <p>{error.message}</p>
      <p className="help">Check that the local API is running, then try again.</p>
      {error.correlationId ? (
        <p className="meta">Correlation ID: {error.correlationId}</p>
      ) : null}
    </section>
  );
}
function toApiError(caught: unknown): CareerPilotApiError {
  return caught instanceof CareerPilotApiError
    ? caught
    : new CareerPilotApiError(
        "The local API is unavailable. Your entered data remains in this tab; reconnect and try again.",
      );
}
