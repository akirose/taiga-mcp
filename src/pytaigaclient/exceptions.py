import requests


class TaigaException(Exception):
    """Base exception for Taiga API client errors."""
    pass


class TaigaAPIError(TaigaException):
    """Represents an error returned by the Taiga API."""

    def __init__(self, status_code: int, response: requests.Response):
        self.status_code = status_code
        self.response = response
        try:
            self.error_detail = response.json().get(
                '_error_message', 'No error message provided by API.')
        except requests.exceptions.JSONDecodeError:
            self.error_detail = response.text or "Non-JSON error response."
        super().__init__(f"API Error {status_code}: {self.error_detail}")


class TaigaAuthenticationError(TaigaAPIError):
    """Raised for authentication failures (401, 403)."""
    pass


class TaigaNotFoundError(TaigaAPIError):
    """Raised when a resource is not found (404)."""
    pass


class TaigaBadRequestError(TaigaAPIError):
    """Raised for bad requests (400)."""
    pass


class TaigaConcurrencyError(TaigaAPIError):
    """Raised for optimistic concurrency control failures (409)."""
    pass


class TaigaRateLimitError(TaigaAPIError):
    """Raised when rate limit is exceeded (429)."""
    pass


class TaigaServerError(TaigaAPIError):
    """Raised for server-side errors (5xx)."""
    pass


def handle_api_error(response: requests.Response):
    """Raises the appropriate TaigaAPIError based on status code."""
    status_code = response.status_code
    if 400 <= status_code < 500:
        if status_code in (401, 403):
            raise TaigaAuthenticationError(status_code, response)
        elif status_code == 404:
            raise TaigaNotFoundError(status_code, response)
        elif status_code == 409:
            raise TaigaConcurrencyError(status_code, response)
        elif status_code == 429:
            raise TaigaRateLimitError(status_code, response)
        else:  # Generic 4xx
            raise TaigaBadRequestError(status_code, response)
    elif 500 <= status_code < 600:
        raise TaigaServerError(status_code, response)
    else:
        # Should not happen if called correctly, but handle just in case
        raise TaigaAPIError(status_code, response)
