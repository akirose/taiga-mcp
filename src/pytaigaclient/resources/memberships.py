from typing import Any, Dict, List, Optional

from .base import Resource


class Memberships(Resource):
    """
    Handles operations related to Project Memberships and Invitations in Taiga.

    Note: The API documentation refers to this as section 11.
    See https://docs.taiga.io/api.html#memberships-invitations
    """

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List memberships (or invitations).

        Args:
            query_params: Dictionary of query parameters (e.g., project, role).

        Returns:
            List of membership/invitation detail objects.
        """
        endpoint = "/memberships"
        result = self.client.get(endpoint, params=query_params)
        return result if isinstance(result, list) else []

    def create(
        self, project: int, role: int, username: str
    ) -> Dict[str, Any]:
        """
        Create a new membership or send an invitation if the user does not exist
        or is not active.

        Args:
            project: Project ID.
            role: Role ID to assign.
            username: Username or email address of the user to invite/add.

        Returns:
            The newly created membership or invitation detail object.
        """
        endpoint = "/memberships"
        payload = {"project": project, "role": role, "username": username}
        return self.client.post(endpoint, json=payload)

    def bulk_create(
        self, project_id: int, bulk_memberships: List[Dict[str, Any]], invitation_extra_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Create multiple memberships/invitations at once.

        Args:
            project_id: Project ID.
            bulk_memberships: List of dictionaries, each with 'role_id' and 'username'.
                              Example: [{'role_id': 3, 'username': 'test@test.com'}]
            invitation_extra_text: Optional additional text for invitation emails.

        Returns:
            List of newly created membership/invitation detail objects.
        """
        endpoint = "/memberships/bulk_create"
        payload: Dict[str, Any] = {
            "project_id": project_id,
            "bulk_memberships": bulk_memberships
        }
        if invitation_extra_text is not None:
            payload["invitation_extra_text"] = invitation_extra_text
        result = self.client.post(endpoint, json=payload)
        return result if isinstance(result, list) else []

    def get(self, membership_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific membership or invitation by its ID.

        Args:
            membership_id: The ID of the membership/invitation.

        Returns:
            Membership/invitation detail object.
        """
        endpoint = f"/memberships/{membership_id}"
        return self.client.get(endpoint)

    def edit(self, membership_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit a membership (partial update).
        Typically used to change the role or other membership properties.

        Args:
            membership_id: The ID of the membership.
            data: Dictionary of attributes to update (e.g., role).

        Returns:
            The updated membership detail object.
        """
        endpoint = f"/memberships/{membership_id}"
        return self.client.patch(endpoint, json=data)

    def update(self, membership_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a membership (full update). Use with caution.

        Args:
            membership_id: The ID of the membership.
            data: Dictionary representing the full membership object.

        Returns:
            The updated membership detail object.
        """
        endpoint = f"/memberships/{membership_id}"
        return self.client.put(endpoint, json=data)

    def delete(self, membership_id: int) -> Optional[Any]:
        """
        Delete a membership or revoke an invitation.

        Args:
            membership_id: The ID of the membership/invitation to delete.

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = f"/memberships/{membership_id}"
        return self.client.delete(endpoint)

    def resend_invitation(self, membership_id: int) -> Dict[str, Any]:
        """
        Resend an invitation email for a pending membership.

        Args:
            membership_id: The ID of the invitation (pending membership).

        Returns:
            The membership/invitation detail object.
        """
        endpoint = f"/memberships/{membership_id}/resend_invitation"
        return self.client.post(endpoint)

    # --- Invitation Specific (using /invitations endpoint) ---

    def get_invitation_by_token(self, token: str) -> Dict[str, Any]:
        """
        Retrieve details of an invitation using its token.

        Args:
            token: The invitation token (UUID string).

        Returns:
            Invitation detail object (similar structure to membership).
        """
        endpoint = f"/invitations/{token}"
        return self.client.get(endpoint)
