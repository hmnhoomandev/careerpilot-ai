"""Production-semantics tests requiring an explicitly disposable PostgreSQL URL."""

from __future__ import annotations

import os
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from careerpilot_api.database import PostgresProfileRepository, create_postgres_engine
from careerpilot_api.main import create_app
from careerpilot_core import AuthorizationContext, ProfessionalProfile, Role, Skill
from careerpilot_core.ports import StaleProfileVersionError
from tests.api.helpers import login_headers

if TYPE_CHECKING:
    from collections.abc import Iterator

DATABASE_URL = os.environ.get("CAREERPILOT_TEST_DATABASE_URL")
pytestmark = pytest.mark.postgres


@pytest.fixture
def repository() -> Iterator[PostgresProfileRepository]:
    if not DATABASE_URL:
        pytest.skip("CAREERPILOT_TEST_DATABASE_URL is not set")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_postgres_engine(DATABASE_URL)
    yield PostgresProfileRepository(engine)
    engine.dispose()


def context(tenant_id: str) -> AuthorizationContext:
    return AuthorizationContext(
        actor_id=f"actor-{tenant_id}",
        tenant_id=tenant_id,
        role=Role.OWNER,
        purpose="personal_career_support",
        correlation_id="postgres-integration",
    )


def test_postgres_persistence_tenant_isolation_and_concurrency(
    repository: PostgresProfileRepository,
) -> None:
    assert DATABASE_URL is not None
    ada = context("tenant-ada")
    grace = context("tenant-grace")
    profile = ProfessionalProfile(
        profile_id="profile-integration",
        tenant_id=ada.tenant_id,
        owner_actor_id=ada.actor_id,
        display_name="Ada Example",
        professional_summary="Synthetic integration profile summary.",
    )
    repository.save(profile, ada)
    assert repository.get(profile.profile_id, grace) is None

    restarted_engine = create_postgres_engine(DATABASE_URL)
    restarted_repository = PostgresProfileRepository(restarted_engine)
    assert restarted_repository.get(profile.profile_id, ada) == profile
    restarted_engine.dispose()

    invalid = replace(profile, skills=(Skill("Python"), Skill("Python")))
    with pytest.raises(IntegrityError):
        repository.update(invalid, 1, ada)
    after_rollback = repository.get(profile.profile_id, ada)
    assert after_rollback is not None
    assert after_rollback.version == 1

    saved = repository.update(profile, 1, ada)
    assert saved.version == 2
    with pytest.raises(StaleProfileVersionError):
        repository.update(profile, 1, ada)


def test_api_profile_survives_application_restart(
    repository: PostgresProfileRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    del repository
    assert DATABASE_URL is not None
    monkeypatch.setenv("CAREERPILOT_DATABASE_URL", DATABASE_URL)
    with TestClient(create_app()) as first_client:
        headers = login_headers(first_client, "ada", "tenant-ada")
        created = first_client.post(
            "/api/v1/profiles",
            headers=headers,
            json={
                "display_name": "Persistent Ada",
                "professional_summary": "Synthetic persistence restart test profile.",
            },
        )
        assert created.status_code == 201
        profile_id = created.json()["profile_id"]

    with TestClient(create_app()) as restarted_client:
        restarted_headers = login_headers(restarted_client, "ada", "tenant-ada")
        loaded = restarted_client.get(
            f"/api/v1/profiles/{profile_id}", headers=restarted_headers
        )
    assert loaded.status_code == 200
    assert loaded.json()["display_name"] == "Persistent Ada"
