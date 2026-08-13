"""Stable failure vocabulary; provider details never cross the service boundary."""


class SpecialistError(RuntimeError):
    code = "specialist_error"


class SpecialistUnavailableError(SpecialistError):
    code = "specialist_unavailable"


class TransferNotAuthorizedError(SpecialistError):
    code = "external_transfer_not_authorized"


class ProviderTimeoutError(SpecialistError):
    code = "provider_timeout"


class ProviderQuotaExceededError(SpecialistError):
    code = "provider_quota_exceeded"


class ProviderOutageError(SpecialistError):
    code = "provider_outage"


class MalformedProviderOutputError(SpecialistError):
    code = "malformed_provider_output"
