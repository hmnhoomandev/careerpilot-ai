"""Framework-independent values for the deterministic walking skeleton."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProfessionalProfile:
    """A minimal local profile; richer evidence belongs to Phase 4."""

    profile_id: str
    tenant_id: str
    owner_actor_id: str
    display_name: str
    professional_summary: str


@dataclass(frozen=True, slots=True)
class JobAnalysis:
    """A deterministic placeholder result, never a model-generated assessment."""

    analysis_id: str
    profile_id: str
    tenant_id: str
    headline: str
    summary: str
    shared_terms: tuple[str, ...]
    disclaimer: str
