import requests
import logging
from typing import Optional, Dict, Any, List, Union, IO
from urllib.parse import urljoin

from .exceptions import TaigaException, handle_api_error
from .resources.auth import Auth
from .resources.projects import Projects
from .resources.milestones import Milestones
from .resources.user_stories import UserStories
from .resources.tasks import Tasks
from .resources.issues import Issues
from .resources.wiki import Wiki
from .resources.memberships import Memberships
from .resources.users import Users
from .resources.issue_statuses import IssueStatuses
from .resources.issue_types import IssueTypes
from .resources.issue_priorities import IssuePriorities
from .resources.issue_severities import IssueSeverities
from .resources.epics import Epics
from .resources.points import Points
from .resources.userstory_statuses import UserStoryStatuses
from .resources.custom_attributes import (
    UserStoryCustomAttributes, TaskCustomAttributes,
    IssueCustomAttributes, EpicCustomAttributes
)
from .resources.webhooks import Webhooks
from .resources.search import Search
from .resources.timeline import Timeline

logger = logging.getLogger(__name__)


class TaigaClient:
    """
    Main client class for interacting with the Taiga API.
    """
    DEFAULT_API_VERSION = "/api/v1/"

    def __init__(
        self,
        host: str,
        auth_token: Optional[str] = None,
        token_type: str = "Bearer",  # Or "Application"
        api_version: str = DEFAULT_API_VERSION,
        session: Optional[requests.Session] = None,
        default_timeout: int = 30,
        accept_language: str = "en",
        disable_pagination: bool = False,
    ):
        """
        Initializes the TaigaClient.

        Args:
            host: The base URL of the Taiga instance (e.g., "https://api.taiga.io").
            auth_token: The authentication token (Bearer or Application).
            token_type: Type of the token ("Bearer" or "Application").
            api_version: The API version path (default: "/api/v1/").
            session: An optional requests.Session object.
            default_timeout: Default timeout for requests in seconds.
            accept_language: Default 'Accept-Language' header value.
            disable_pagination: If True, sets the 'x-disable-pagination' header.
        """
        if not host:
            raise ValueError("Taiga host URL cannot be empty.")
        self.host = host.rstrip('/')
        self.api_base_url = urljoin(self.host, api_version.strip('/') + '/')
        self.auth_token = auth_token
        self.token_type = token_type
        self.session = session or requests.Session()
        self.default_timeout = default_timeout
        self.accept_language = accept_language
        self.disable_pagination = disable_pagination

        self._update_session_headers()

        # Initialize resource endpoints
        self.auth = Auth(self)
        self.projects = Projects(self)
        self.milestones = Milestones(self)
        self.user_stories = UserStories(self)
        self.tasks = Tasks(self)
        self.issues = Issues(self)
        self.wiki = Wiki(self)
        self.memberships = Memberships(self)
        self.users = Users(self)
        self.issue_statuses = IssueStatuses(self)
        self.issue_types = IssueTypes(self)
        self.issue_priorities = IssuePriorities(self)
        self.issue_severities = IssueSeverities(self)

        # New resources
        self.epics = Epics(self)
        self.points = Points(self)
        self.userstory_statuses = UserStoryStatuses(self)
        self.webhooks = Webhooks(self)
        self.search = Search(self)
        self.timeline = Timeline(self)

        # Custom attributes
        self.userstory_custom_attributes = UserStoryCustomAttributes(self)
        self.task_custom_attributes = TaskCustomAttributes(self)
        self.issue_custom_attributes = IssueCustomAttributes(self)
        self.epic_custom_attributes = EpicCustomAttributes(self)

    def update_token(self, auth_token: Optional[str], token_type: str = "Bearer"):
        """Updates the authentication token and type."""
        self.auth_token = auth_token
        self.token_type = token_type
        self._update_session_headers()

    def _update_session_headers(self):
        """Updates the common headers in the session."""
        self.session.headers["Accept-Language"] = self.accept_language
        # Expect JSON responses
        self.session.headers["Accept"] = "application/json"
        if self.disable_pagination:
            self.session.headers["x-disable-pagination"] = "True"
        else:
            self.session.headers.pop("x-disable-pagination", None)

        if self.auth_token:
            self.session.headers["Authorization"] = f"{self.token_type} {self.auth_token}"
        else:
            self.session.headers.pop("Authorization", None)

    def _build_url(self, path: str) -> str:
        """Builds the full API URL for a given path."""
        return urljoin(self.api_base_url, path.lstrip('/'))

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        # requests uses 'json' for auto-serialization
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Union[IO, tuple]]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        raise_exception: bool = True
    ) -> Optional[Union[Dict, List, Any]]:
        """
        Makes an HTTP request to the Taiga API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            path: API endpoint path (e.g., "/projects", "/users/me").
            params: URL query parameters.
            data: Data for POST/PUT/PATCH (typically form-encoded, used with files).
            json: Data for POST/PUT/PATCH (automatically JSON-encoded).
            files: Dictionary for multipart file uploads.
            headers: Additional request headers.
            timeout: Request timeout in seconds.
            raise_exception: Whether to raise TaigaAPIError on failure.

        Returns:
            Decoded JSON response if successful and content exists, otherwise None.

        Raises:
            TaigaAPIError or its subclasses on API errors if raise_exception is True.
            requests.exceptions.RequestException on connection errors.
        """
        full_url = self._build_url(path)
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        # Ensure Content-Type is set correctly for JSON data, unless files are present
        if json is not None and not files:
            request_headers["Content-Type"] = "application/json"
        elif files:
            # requests handles multipart Content-Type automatically when files are present
            # remove explicit Content-Type if it was set for json
            request_headers.pop("Content-Type", None)
        elif data is not None and not files:
            # Default to json if data is dict and no files
            request_headers["Content-Type"] = "application/json"
            json = data  # Move data to json param for requests
            data = None

        logger.debug(f"Request: {method} {full_url}")
        logger.debug(f"Params: {params}")
        logger.debug(f"Data: {data}")
        logger.debug(f"Json: {json}")
        logger.debug(f"Headers: {request_headers}")

        try:
            response = self.session.request(
                method=method,
                url=full_url,
                params=params,
                data=data,
                json=json,
                files=files,
                headers=request_headers,
                timeout=timeout or self.default_timeout
            )

            logger.debug(f"Response Status: {response.status_code}")
            # Log response body carefully, might be large
            # logger.debug(f"Response Body: {response.text[:500]}...")

            if not response.ok:
                logger.error(
                    f"API Error: {response.status_code} - {response.text}")
                if raise_exception:
                    handle_api_error(response)
                return None  # Or response object itself if needed?

            if response.status_code == 204:  # No Content
                return None

            # Handle potential non-JSON success responses if necessary
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                logger.warning(
                    f"Non-JSON success response received for {method} {full_url}")
                return response.text  # Or handle differently if needed

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise TaigaException(f"Request failed: {e}") from e

    # Convenience methods
    def get(self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Union[Dict, List, Any]]:
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Union[Dict, List, Any]]:
        # Prioritize json if both data and json are provided non-None, common usage pattern
        if json is not None:
            data = None
        return self._request("POST", path, data=data, json=json, files=files, **kwargs)

    def patch(self, path: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Union[Dict, List, Any]]:
        if json is not None:
            data = None
        return self._request("PATCH", path, data=data, json=json, **kwargs)

    def put(self, path: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Union[Dict, List, Any]]:
        if json is not None:
            data = None
        return self._request("PUT", path, data=data, json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> Optional[Union[Dict, List, Any]]:
        return self._request("DELETE", path, **kwargs)
