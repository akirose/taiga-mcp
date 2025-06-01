# taiga_client/resources/auth.py

from typing import TYPE_CHECKING, Optional, Dict, Any, cast

if TYPE_CHECKING:
    # Avoid circular import for type hinting
    from pytaigaclient.client import TaigaClient


class Auth:
    """
    Handles authentication and registration related endpoints for the Taiga API.
    """

    def __init__(self, client: 'TaigaClient'):
        """
        Initializes the Auth resource.

        Args:
            client: The TaigaClient instance.
        """
        self._client = client

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Performs normal login using username/email and password.
        Updates the client's token upon successful authentication.

        Ref: 3.1. Normal login

        Args:
            username: The user's username or email address.
            password: The user's password.

        Returns:
            A dictionary containing the authentication details (token, user info, etc.).

        Raises:
            TaigaAuthenticationError: If login fails.
            TaigaAPIError: For other API-related errors.
            TaigaException: For connection errors.
        """
        payload = {
            "type": "normal",
            "username": username,
            "password": password
        }
        # Auth endpoint doesn't require prior authentication token
        current_auth = self._client.session.headers.pop("Authorization", None)
        try:
            # Use cast to inform the type checker about the expected type
            response_data = cast(Dict[str, Any], self._client.post(
                "/auth", json=payload))  # Use client's _request method
            if response_data and 'auth_token' in response_data:
                auth_token: str = response_data['auth_token']
                self._client.update_token(
                    auth_token=auth_token,
                    token_type="Bearer"  # Normal login uses Bearer token
                )
                # Optionally store refresh token if needed for auto-refresh logic
                # self._client.refresh_token = response_data.get('refresh')
            return response_data
        finally:
            # Restore auth header if it existed or if login succeeded
            if current_auth:
                self._client.session.headers["Authorization"] = current_auth
            elif self._client.auth_token:
                self._client.session.headers[
                    "Authorization"] = f"{self._client.token_type} {self._client.auth_token}"

    def login_github(self, code: str, invitation_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Performs login using a GitHub authorization code.
        Updates the client's token upon successful authentication.

        Ref: 3.2. Github login

        Args:
            code: The authorization code obtained from GitHub's OAuth flow.
            invitation_token: Optional token for accepting project invitations during login.

        Returns:
            A dictionary containing the authentication details.

        Raises:
            TaigaAuthenticationError: If login fails.
            TaigaAPIError: For other API-related errors.
            TaigaException: For connection errors.
        """
        payload = {
            "type": "github",
            "code": code
        }
        if invitation_token:
            payload["token"] = invitation_token

        current_auth = self._client.session.headers.pop("Authorization", None)
        try:
            # Use cast to inform the type checker about the expected type
            response_data = cast(
                Dict[str, Any], self._client.post("/auth", json=payload))
            if response_data and 'auth_token' in response_data:
                self._client.update_token(
                    auth_token=response_data['auth_token'],
                    token_type="Bearer"  # Assume GitHub flow also results in a Bearer token
                )
                # self._client.refresh_token = response_data.get('refresh')
            return response_data
        finally:
            if current_auth:
                self._client.session.headers["Authorization"] = current_auth
            elif self._client.auth_token:
                self._client.session.headers[
                    "Authorization"] = f"{self._client.token_type} {self._client.auth_token}"

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refreshes the authentication token using a refresh token.
        Updates the client's token upon success.

        Ref: 3.3. Refresh auth token

        Args:
            refresh_token: The refresh token obtained during initial login.

        Returns:
            A dictionary containing the new 'auth_token' and 'refresh' token.

        Raises:
            TaigaAuthenticationError: If refresh fails.
            TaigaAPIError: For other API-related errors.
            TaigaException: For connection errors.
        """
        payload = {"refresh": refresh_token}
        current_auth = self._client.session.headers.pop("Authorization", None)
        try:
            # Use cast to inform the type checker about the expected type
            response_data = cast(Dict[str, Any], self._client.post(
                "/auth/refresh", json=payload))
            if response_data and 'auth_token' in response_data:
                self._client.update_token(
                    auth_token=response_data['auth_token'],
                    token_type="Bearer"  # Assume refresh provides a Bearer token
                )
                # self._client.refresh_token = response_data.get('refresh') # Update stored refresh token
            return response_data
        finally:
            if current_auth:
                self._client.session.headers["Authorization"] = current_auth
            elif self._client.auth_token:
                self._client.session.headers[
                    "Authorization"] = f"{self._client.token_type} {self._client.auth_token}"

    def register_public(self, username: str, password: str, email: str, full_name: str, accepted_terms: bool = True) -> Dict[str, Any]:
        """
        Registers a new user via public registration (if enabled on the instance).
        Optionally updates the client's token upon successful registration.

        Ref: 3.4. Public registry

        Args:
            username: The desired username.
            password: The desired password.
            email: The user's email address.
            full_name: The user's full name.
            accepted_terms: Whether the terms have been accepted (defaults to True).

        Returns:
            A dictionary containing the authentication details for the newly registered user.

        Raises:
            TaigaBadRequestError: If registration fails due to validation errors (e.g., username taken).
            TaigaAPIError: For other API-related errors.
            TaigaException: For connection errors.
        """
        payload = {
            "type": "public",
            "username": username,
            "password": password,
            "email": email,
            "full_name": full_name,
            "accepted_terms": accepted_terms
        }
        current_auth = self._client.session.headers.pop("Authorization", None)
        try:
            # Use raise_exception=False to potentially handle specific registration errors if needed
            # Use cast to inform the type checker about the expected type
            response_data = cast(Dict[str, Any], self._client.post(
                "/auth/register", json=payload))
            # Decide if registration should automatically log in the user
            # if response_data and 'auth_token' in response_data:
            #    self._client.update_token(response_data['auth_token'], "Bearer")
            return response_data
        finally:
            if current_auth:
                self._client.session.headers["Authorization"] = current_auth
            # Don't restore token if registration happened, as it might grant one

    def register_private(
        self,
        token: str,
        username: str,
        password: str,
        existing: bool,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        accepted_terms: bool = True
    ) -> Dict[str, Any]:
        """
        Registers a user associated with a project invitation or links an existing user.
        Updates the client's token upon successful registration/linking.

        Ref: 3.5. Private registry

        Args:
            token: The invitation token.
            username: The username (required).
            password: The password (required).
            existing: Boolean indicating if the user already exists in the platform.
            email: Required if 'existing' is False.
            full_name: Required if 'existing' is False.
            accepted_terms: Whether the terms have been accepted (defaults to True).

        Returns:
            A dictionary containing the authentication details.

        Raises:
            ValueError: If 'existing' is False but 'email' or 'full_name' are missing.
            TaigaBadRequestError: If registration fails due to validation errors.
            TaigaAPIError: For other API-related errors.
            TaigaException: For connection errors.
        """
        payload = {
            "type": "private",
            "token": token,
            "username": username,
            "password": password,
            "existing": existing,
            "accepted_terms": accepted_terms
        }

        if not existing:
            if not email or not full_name:
                raise ValueError(
                    "Email and full_name are required when 'existing' is False.")
            payload["email"] = email
            payload["full_name"] = full_name
        current_auth = self._client.session.headers.pop("Authorization", None)
        try:
            # Use cast to inform the type checker about the expected type
            response_data = cast(Dict[str, Any], self._client.post(
                "/auth/register", json=payload))
            if response_data and 'auth_token' in response_data:
                self._client.update_token(
                    auth_token=response_data['auth_token'],
                    token_type="Bearer"
                )
                # self._client.refresh_token = response_data.get('refresh')
            return response_data
        finally:
            if current_auth:
                self._client.session.headers["Authorization"] = current_auth
            elif self._client.auth_token:  # Re-add if private reg was successful
                self._client.session.headers[
                    "Authorization"] = f"{self._client.token_type} {self._client.auth_token}"
