"""Stable safe service errors."""


class InterviewError(RuntimeError):
    code = "interview_error"


class InterviewUnavailableError(InterviewError):
    code = "interview_unavailable"


class GuardrailBlockedError(InterviewError):
    code = "guardrail_blocked"


class ApprovalConflictError(InterviewError):
    code = "approval_conflict"


class ExternalTransferDeniedError(InterviewError):
    code = "external_transfer_not_authorized"


class BudgetDeniedError(InterviewError):
    code = "live_budget_not_approved"
