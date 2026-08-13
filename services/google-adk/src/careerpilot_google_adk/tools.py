"""Request-local ADK tool factory; no global source cache exists."""

from collections.abc import Callable

from careerpilot_google_adk.models import SourceExcerpt


def build_source_tool(
    sources: tuple[SourceExcerpt, ...],
) -> Callable[[str], dict[str, str]]:
    by_id = {source.source_id: source for source in sources}

    def read_approved_source(source_id: str) -> dict[str, str]:
        """Read one approved source excerpt by its exact source identifier."""
        source = by_id.get(source_id)
        if source is None:
            return {"status": "denied", "reason": "source_not_allowlisted"}
        return {
            "status": "ok",
            "source_id": source.source_id,
            "title": source.title,
            "content": source.content,
        }

    return read_approved_source
