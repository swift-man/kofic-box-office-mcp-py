class CultureOpenApiError(RuntimeError):
    """Raised when a 문화공공데이터광장 API integration or local validation fails."""


class KoficBoxOfficeError(CultureOpenApiError):
    """Raised when the KOFIC box-office API or local validation fails."""


class ArkoEventError(CultureOpenApiError):
    """Raised when the ARKO event API or local validation fails."""
