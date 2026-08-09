# Product Vision

## Problem

Job seekers assemble profiles, interpret vacancies, tailor documents, and track
applications across fragmented tools. Generic AI assistance can invent claims,
hide its sources, leak personal data, or act without meaningful consent.

## Vision

CareerPilot AI is a trustworthy career workspace that turns verified user
evidence and user-supplied job information into cited analysis, truthful drafts,
and an auditable application workflow controlled by the job seeker.

## Initial persona

**Independent job seeker:** maintains a professional profile, supplies evidence
and vacancies, wants faster application preparation, and must retain control over
what is inferred, generated, stored, shared, or deleted.

## Future personas

- **Career coach:** supports explicitly consenting clients through delegated,
  revocable, least-privilege access.
- **Coach organization administrator:** manages membership and policy without
  inheriting unrestricted access to candidate content.
- **Platform operator:** maintains service health and security without routine
  access to raw personal content.

These personas shape tenancy and authorization now but are not initial features.

## Jobs to be done

1. When preparing an application, help me reuse verified evidence without
   repeatedly reconstructing my history.
2. When reading a vacancy, show how requirements map to my evidence and where I
   have gaps.
3. When drafting a resume or letter, ensure every material claim is supported or
   clearly asks for my confirmation.
4. When an automated process proposes an important action, let me inspect, edit,
   approve, reject, or cancel it.
5. When I question a result, show sources, decision summaries, workflow state,
   and audit history without exposing hidden reasoning.
6. When I exercise privacy rights, make access, correction, export, and deletion
   understandable and reliable.

## First successful journey

Professional profile and evidence → user-supplied job description → grounded job
analysis → cited match → skill gaps → truthful resume draft → truthful cover
letter → human review and approval → application tracking.

Automatic submission and email are excluded from this initial journey.

## Product principles

- Evidence before assertion.
- Human authority before consequence.
- Deterministic code before probabilistic reasoning where rules suffice.
- Least data, least privilege, and least external exposure.
- Explain outcomes and sources, never hidden chain-of-thought.
- Accessible, internationalization-ready interfaces.
- Local and fake-first development under a CHF 0 budget.

## Scope boundaries

### In scope across the roadmap

- Profile and evidence management, job analysis, grounded matching, skill gaps,
  document drafting, approvals, interview support, and application tracking.
- Multi-tenancy, future coach delegation, privacy rights, security, evaluation,
  observability, recovery, and controlled deployment.

### Out of initial success scope

- Automatic application submission or email.
- Unrestricted web scraping.
- Employment, legal, immigration, or medical advice.
- Ranking candidates for employers.
- Claims of legal certification or guaranteed compliance.
- Autonomous decisions that materially affect a person.

## Success statement

A user succeeds when they can complete the first journey with synthetic or their
authorized data, verify every material generated claim, understand uncertainty,
control each consequential step, and recover or delete their data as documented.
