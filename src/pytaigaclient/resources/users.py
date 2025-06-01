from typing import Any, Dict, List, Optional, IO

from .base import Resource


class Users(Resource):
    """
    Handles operations related to Users in Taiga.

    See https://docs.taiga.io/api.html#users
    """

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List users.

        Args:
            query_params: Dictionary of query parameters to filter users.

        Returns:
            List of user detail objects.
        """
        endpoint = "/users"
        result = self.client.get(endpoint, params=query_params)
        return result if isinstance(result, list) else []

    def get(self, user_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific user by ID.

        Args:
            user_id: The ID of the user.

        Returns:
            User detail object.
        """
        endpoint = f"/users/{user_id}"
        return self.client.get(endpoint)

    def get_me(self) -> Dict[str, Any]:
        """
        Retrieve details of the currently authenticated user.

        Returns:
            User detail object for the authenticated user.
        """
        endpoint = "/users/me"
        return self.client.get(endpoint)

    def edit(self, user_id: int, data: Dict[str, Any], version: Optional[int] = None) -> Dict[str, Any]:
        """
        Edit a user profile (partial update).
        Note: API requires version for PATCH/PUT, usually fetched first via GET.

        Args:
            user_id: The ID of the user to edit.
            data: Dictionary of attributes to update (e.g., full_name, bio).
            version: The current version number of the user object (required by API).
                     If None, it attempts to fetch it first (less efficient).

        Returns:
            The updated user detail object.
        """
        endpoint = f"/users/{user_id}"
        if version is None:
            user_data = self.get(user_id)
            version = user_data.get('version')
            if version is None:
                raise ValueError("Could not fetch current user version for edit.")

        payload = {"version": version}
        payload.update(data)
        return self.client.patch(endpoint, json=payload)

    def update(self, user_id: int, data: Dict[str, Any], version: Optional[int] = None) -> Dict[str, Any]:
        """
        Update a user profile (full update). Use with caution.
        Note: API requires version for PATCH/PUT, usually fetched first via GET.

        Args:
            user_id: The ID of the user to update.
            data: Dictionary representing the full user object.
            version: The current version number of the user object (required by API).
                     If None, it attempts to fetch it first (less efficient).

        Returns:
            The updated user detail object.
        """
        endpoint = f"/users/{user_id}"
        if version is None:
            user_data = self.get(user_id)
            version = user_data.get('version')
            if version is None:
                raise ValueError("Could not fetch current user version for update.")

        payload = data.copy()
        payload["version"] = version
        return self.client.put(endpoint, json=payload)

    def delete(self, user_id: int) -> Optional[Any]:
        """
        Delete a user account (requires admin privileges).

        Args:
            user_id: The ID of the user to delete.

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = f"/users/{user_id}"
        return self.client.delete(endpoint)

    def get_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            User statistics object.
        """
        endpoint = f"/users/{user_id}/stats"
        return self.client.get(endpoint)

    def get_watched(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get a list of items watched by the user.

        Args:
            user_id: The ID of the user.

        Returns:
            List of watched item objects.
        """
        endpoint = f"/users/{user_id}/watched"
        result = self.client.get(endpoint)
        return result if isinstance(result, list) else []

    def get_liked(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get a list of items liked by the user.

        Args:
            user_id: The ID of the user.

        Returns:
            List of liked item objects.
        """
        endpoint = f"/users/{user_id}/liked"
        result = self.client.get(endpoint)
        return result if isinstance(result, list) else []

    def get_voted(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get a list of items voted on by the user.

        Args:
            user_id: The ID of the user.

        Returns:
            List of voted item objects.
        """
        endpoint = f"/users/{user_id}/voted"
        result = self.client.get(endpoint)
        return result if isinstance(result, list) else []

    def get_contacts(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get the contact list for a user.

        Args:
            user_id: The ID of the user.

        Returns:
            List of contact (user) objects.
        """
        endpoint = f"/users/{user_id}/contacts"
        result = self.client.get(endpoint)
        return result if isinstance(result, list) else []

    def cancel_account(self, password: str) -> Optional[Any]:
        """
        Cancel the authenticated user's account.

        Args:
            password: The user's current password for confirmation.

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = "/users/cancel"
        payload = {"password": password}
        return self.client.post(endpoint, json=payload)

    def change_avatar(self, avatar_file: IO) -> Dict[str, Any]:
        """
        Change the avatar for the authenticated user.

        Args:
            avatar_file: File object containing the new avatar image.

        Returns:
            Updated user detail object.
        """
        endpoint = "/users/change_avatar"
        files = {'avatar': avatar_file}
        # Note: API expects multipart/form-data, not JSON
        return self.client.post(endpoint, files=files)

    def remove_avatar(self) -> Dict[str, Any]:
        """
        Remove the avatar for the authenticated user.

        Returns:
            Updated user detail object.
        """
        endpoint = "/users/remove_avatar"
        return self.client.post(endpoint)

    def change_email(self, current_password: str, new_email: str) -> Optional[Any]:
        """
        Change the email address for the authenticated user.

        Args:
            current_password: The user's current password.
            new_email: The new email address.

        Returns:
            None if successful (typically HTTP 204 or similar).
        """
        endpoint = "/users/change_email"
        payload = {"password": current_password, "email": new_email}
        return self.client.post(endpoint, json=payload)

    def change_password(self, current_password: str, new_password1: str, new_password2: str) -> Optional[Any]:
        """
        Change the password for the authenticated user.

        Args:
            current_password: The user's current password.
            new_password1: The new password.
            new_password2: The new password confirmation (must match new_password1).

        Returns:
            None if successful (typically HTTP 204 or similar).
        """
        endpoint = "/users/change_password"
        payload = {
            "old_password": current_password,
            "password": new_password1,
            "password_confirmation": new_password2
        }
        return self.client.post(endpoint, json=payload)

    # Password recovery is usually handled outside direct API calls from a library
    # as it involves email tokens, so omitting those for now.
