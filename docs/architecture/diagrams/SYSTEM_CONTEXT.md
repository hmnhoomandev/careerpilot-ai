# System Context Diagram

```mermaid
C4Context
    title CareerPilot AI System Context
    Person(jobSeeker, "Job Seeker", "Controls profile, evidence, drafts, approvals, and applications")
    Person(coach, "Future Career Coach", "Receives explicit delegated access; not initially active")
    System(careerPilot, "CareerPilot AI", "Evidence-grounded career intelligence and application workspace")
    System_Ext(identity, "OIDC Identity Provider", "Authentication; Google Identity Platform reference")
    System_Ext(models, "Authorized Model Providers", "Gemini and bounded OpenAI service")
    System_Ext(sources, "Permitted Data Sources", "User input and approved APIs only")
    System_Ext(cloud, "Google Cloud", "Future Zurich-first managed runtime and data services")

    Rel(jobSeeker, careerPilot, "Uses and approves", "HTTPS")
    Rel(coach, careerPilot, "Future scoped delegation", "HTTPS")
    Rel(careerPilot, identity, "Authenticates via", "OIDC")
    Rel(careerPilot, models, "Sends minimized authorized requests", "TLS")
    Rel(careerPilot, sources, "Retrieves permitted data", "Approved API")
    Rel(careerPilot, cloud, "Future deployment", "Private/authenticated services")
```

Trust assumption: every external actor, document, provider response, network, and
service identity is untrusted until authenticated, authorized, validated, and
bounded by purpose.
