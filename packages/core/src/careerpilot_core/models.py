"""Framework-independent professional-profile and evidence values."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True, slots=True)
class Skill:
    """A user-asserted skill; verification is represented explicitly."""

    name: str
    verified: bool = False


@dataclass(frozen=True, slots=True)
class Experience:
    """A truthful user-supplied employment or project experience."""

    title: str
    organization: str
    start_date: str
    end_date: str | None
    description: str


@dataclass(frozen=True, slots=True)
class Education:
    """A user-supplied education record."""

    institution: str
    qualification: str
    start_date: str | None = None
    end_date: str | None = None


@dataclass(frozen=True, slots=True)
class ProfessionalProfile:
    """Tenant-owned professional profile with a stale-write guard."""

    profile_id: str
    tenant_id: str
    owner_actor_id: str
    display_name: str
    professional_summary: str
    version: int = 1
    skills: tuple[Skill, ...] = ()
    experiences: tuple[Experience, ...] = ()
    education: tuple[Education, ...] = ()
    deleted_at: datetime | None = None
    purge_after: datetime | None = None


class EvidenceState(StrEnum):
    """Security lifecycle for evidence before document processing."""

    QUARANTINED = "quarantined"
    SCAN_PENDING = "scan_pending"
    CLEAN = "clean"
    REJECTED = "rejected"
    DELETED = "deleted"


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    """Minimized metadata for evidence; raw bytes are outside this phase."""

    evidence_id: str
    tenant_id: str
    owner_actor_id: str
    profile_id: str
    title: str
    filename: str
    media_type: str
    size_bytes: int
    state: EvidenceState
    version: int = 1
    deleted_at: datetime | None = None
    purge_after: datetime | None = None


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
