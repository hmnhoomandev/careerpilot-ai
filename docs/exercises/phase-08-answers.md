# Phase 8 Exercise Answers

1. Version identifies the record; the hash proves the exact reviewed content.
2. Human consent to old content cannot authorize changed content.
3. The checkpoint resumes code execution; PostgreSQL records the authoritative decision.
4. UI data is attacker-controlled input; the server must authenticate, authorize, and
   validate version, hash, revision, and transition.
5. Temporal should schedule expiry because timers and durable waits are business
   workflow concerns, not in-process graph routing.
