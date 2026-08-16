# User guide

## Before you begin

The current release candidate is a local learning product using synthetic identities.
It is not production authentication and must not receive a real resume or sensitive
personal data. Start the local stack with `make dev`, open `http://127.0.0.1:3000`, and
choose Ada for the complete owner journey.

## Main journey

1. **Profile and evidence:** create or edit the professional profile. Upload only a
   synthetic UTF-8 text or text-based PDF. The product validates, scans locally, indexes
   and labels retrieved text untrusted.
2. **Job workspace:** paste a synthetic job description. Analysis extracts requirements,
   finds cited evidence, shows supported matches, missing/uncertain gaps and a concise
   explanation. Missing evidence must never become a claimed qualification.
3. **Draft review:** generate the resume and cover-letter demonstration. Open citations
   for material claims. Unsupported edits are blocked or remain confirmation requests.
4. **Approval:** review the exact version/hash. Approve, edit-and-approve, reject, request
   information, cancel or allow expiry. Approval does not submit an application or email.
5. **Interview and tracking:** use the labelled local interview modes and application
   tracking presentation. Automatic submission and sending remain disabled.
6. **Notifications, audit and metrics:** load only when needed. Confirm correlation IDs,
   safe decision summaries and metadata-only platform metrics; hidden reasoning is absent.
7. **Privacy controls:** inspect inventory/export, request correction or consent withdrawal,
   and rehearse recoverable deletion. Final legal processing and physical purge are not claimed.

## Safety and accessibility

Use keyboard navigation from the skip link through every control; visible focus and status
messages should remain available at 375px, desktop and 200% zoom. If a citation, permission,
service or connection is unavailable, stop and use the visible correlation ID—never bypass
authorization or substitute an uncited fact.

To stop, press Control-C in the development terminal. Local in-memory data disappears;
configured PostgreSQL data persists according to the developer/operator setup.
