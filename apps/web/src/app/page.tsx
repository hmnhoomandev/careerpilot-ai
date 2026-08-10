"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { CareerPilotApiError, runDeterministicJourney } from "../lib/careerpilot-api";
import type { AnalysisResult } from "../lib/careerpilot-api";

export default function HomePage() {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<CareerPilotApiError | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAnalysis(null);
    setError(null);
    setSubmitting(true);
    const data = new FormData(event.currentTarget);
    try {
      const result = await runDeterministicJourney({
        displayName: String(data.get("displayName")),
        professionalSummary: String(data.get("professionalSummary")),
        jobDescription: String(data.get("jobDescription")),
      });
      setAnalysis(result);
    } catch (caught) {
      setError(
        caught instanceof CareerPilotApiError
          ? caught
          : new CareerPilotApiError("The local API is unavailable. Please try again."),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <header className="hero">
        <p className="eyebrow">CareerPilot AI · Local deterministic preview</p>
        <h1>Compare your profile with a job description</h1>
        <p className="lede">
          Enter synthetic data only. This Phase 2 preview compares exact words; it does
          not call an AI model or infer your suitability.
        </p>
      </header>

      <section className="panel" aria-labelledby="journey-heading">
        <h2 id="journey-heading">Your local inputs</h2>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="displayName">Display name</label>
            <input
              id="displayName"
              name="displayName"
              minLength={2}
              maxLength={100}
              autoComplete="name"
              required
              defaultValue="Ada Example"
            />
          </div>

          <div className="field">
            <label htmlFor="professionalSummary">Professional summary</label>
            <p id="summary-help" className="help">
              20–1,000 characters. Do not enter real personal or sensitive data.
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
              50–5,000 characters from a synthetic or explicitly permitted source.
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
            {submitting ? "Comparing…" : "Run deterministic comparison"}
          </button>
        </form>
      </section>

      <div aria-live="polite" aria-atomic="true">
        {error ? (
          <section className="panel error" aria-labelledby="error-heading">
            <h2 id="error-heading">We could not complete the comparison</h2>
            <p>{error.message}</p>
            {error.correlationId ? (
              <p className="meta">Correlation ID: {error.correlationId}</p>
            ) : null}
          </section>
        ) : null}

        {analysis ? (
          <section className="panel result" aria-labelledby="result-heading">
            <p className="eyebrow">Deterministic result</p>
            <h2 id="result-heading">{analysis.headline}</h2>
            <p>{analysis.summary}</p>
            {analysis.shared_terms.length > 0 ? (
              <>
                <h3>Exact shared terms</h3>
                <ul className="terms">
                  {analysis.shared_terms.map((term) => (
                    <li key={term}>{term}</li>
                  ))}
                </ul>
              </>
            ) : null}
            <p className="disclaimer">{analysis.disclaimer}</p>
            <p className="meta">Correlation ID: {analysis.correlation_id}</p>
          </section>
        ) : null}
      </div>
    </main>
  );
}
