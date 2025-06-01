from typing import Any, Dict, List, Optional, Union, IO

from .base import Resource


class Issues(Resource):
    """
    Handles operations related to Issues in Taiga.

    See https://docs.taiga.io/api.html#issues
    """

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List issues.

        Args:
            query_params: Dictionary of query parameters to filter/order issues
                          (e.g., project, status, severity, priority, tags, owner,
                           assigned_to, type, order_by).

        Returns:
            List of issue detail list objects.
        """
        endpoint = "/issues"
        result = self.client.get(endpoint, params=query_params)
        return result if isinstance(result, list) else []

    def create(
        self, project: int, subject: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue.

        Args:
            project: Project ID.
            subject: Issue subject.
            data: Dictionary containing other issue attributes (e.g., status,
                  severity, priority, type, assigned_to, description, tags, milestone).

        Returns:
            The newly created issue detail object.
        """
        endpoint = "/issues"
        payload = {"project": project, "subject": subject}
        if data:
            payload.update(data)
        result = self.client.post(endpoint, json=payload)
        return result if isinstance(result, dict) else {}

    def get(self, issue_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific issue by its ID.

        Args:
            issue_id: The ID of the issue.

        Returns:
            Issue detail object.
        """
        endpoint = f"/issues/{issue_id}"
        result = self.client.get(endpoint)
        return result if isinstance(result, dict) else {}

    def get_by_ref(
        self, ref: int, project: Union[int, str]
    ) -> Dict[str, Any]:
        """
        Retrieve details of an issue by its reference number and project ID/slug.

        Args:
            ref: The reference number of the issue.
            project: The project ID or slug.

        Returns:
            Issue detail object.
        """
        endpoint = "/issues/by_ref"
        params: Dict[str, Union[int, str]] = {"ref": ref}
        if isinstance(project, int):
            params["project"] = project
        else:
            # Docs mention project__slug, API might differ slightly from US/Task
            params["project__slug"] = project
        result = self.client.get(endpoint, params=params)
        return result if isinstance(result, dict) else {}

    def edit(self, issue_id: int, version: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit an issue (partial update).

        Args:
            issue_id: The ID of the issue.
            version: The current version number of the issue for optimistic locking.
            data: Dictionary of attributes to update.

        Returns:
            The updated issue detail object.
        """
        endpoint = f"/issues/{issue_id}"
        payload = {"version": version}
        payload.update(data)
        result = self.client.patch(endpoint, json=payload)
        return result if isinstance(result, dict) else {}

    def update(self, issue_id: int, version: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an issue (full update). Use with caution.

        Args:
            issue_id: The ID of the issue.
            version: The current version number of the issue.
            data: Dictionary representing the full issue object.

        Returns:
            The updated issue detail object.
        """
        endpoint = f"/issues/{issue_id}"
        payload = data.copy()
        payload["version"] = version
        result = self.client.put(endpoint, json=payload)
        return result if isinstance(result, dict) else {}

    def delete(self, issue_id: int) -> Optional[Any]:
        """
        Delete an issue.

        Args:
            issue_id: The ID of the issue to delete.

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = f"/issues/{issue_id}"
        return self.client.delete(endpoint)

    def filters_data(self, project: int) -> Dict[str, Any]:
        """
        Get data for filtering issues within a project.

        Args:
            project: The project ID.

        Returns:
            Issue filters data object.
        """
        endpoint = "/issues/filters_data"
        params = {"project": project}
        result = self.client.get(endpoint, params=params)
        return result if isinstance(result, dict) else {}

    def upvote(self, issue_id: int) -> Optional[Any]:
        """
        Vote for an issue.

        Args:
            issue_id: The ID of the issue to vote for.

        Returns:
            None if successful (HTTP 200 OK with empty body).
        """
        endpoint = f"/issues/{issue_id}/upvote"
        return self.client.post(endpoint)

    def downvote(self, issue_id: int) -> Optional[Any]:
        """
        Remove vote from an issue.

        Args:
            issue_id: The ID of the issue to remove the vote from.

        Returns:
            None if successful (HTTP 200 OK with empty body).
        """
        endpoint = f"/issues/{issue_id}/downvote"
        return self.client.post(endpoint)

    def list_voters(self, issue_id: int) -> List[Dict[str, Any]]:
        """
        Get the list of voters for an issue.

        Args:
            issue_id: The ID of the issue.

        Returns:
            List of issue voter detail objects.
        """
        endpoint = f"/issues/{issue_id}/voters"
        result = self.client.get(endpoint)
        return result if isinstance(result, list) else []

    def watch(self, issue_id: int) -> Optional[Any]:
        """
        Watch an issue.

        Args:
            issue_id: The ID of the issue to watch.

        Returns:
            None if successful (HTTP 200 OK with empty body).
        """
        endpoint = f"/issues/{issue_id}/watch"
        return self.client.post(endpoint)

    def unwatch(self, issue_id: int) -> Optional[Any]:
        """
        Stop watching an issue.

        Args:
            issue_id: The ID of the issue to stop watching.

        Returns:
            None if successful (HTTP 200 OK with empty body).
        """
        endpoint = f"/issues/{issue_id}/unwatch"
        return self.client.post(endpoint)

    def list_watchers(self, issue_id: int) -> List[Dict[str, Any]]:
        """
        Get the list of watchers for an issue.

        Args:
            issue_id: The ID of the issue.

        Returns:
            List of issue watcher objects.
        """
        endpoint = f"/issues/{issue_id}/watchers"
        result = self.client.get(endpoint)
        return result if isinstance(result, list) else []

    # --- Attachment Methods ---

    def list_attachments(self, project: int, object_id: int) -> List[Dict[str, Any]]:
        """
        List attachments for a specific issue.

        Args:
            project: Project ID.
            object_id: Issue ID.

        Returns:
            List of attachment detail objects.
        """
        endpoint = "/issues/attachments"
        params = {"project": project, "object_id": object_id}
        result = self.client.get(endpoint, params=params)
        return result if isinstance(result, list) else []

    def create_attachment(
        self, project: int, object_id: int, attached_file: IO, description: Optional[str] = None, is_deprecated: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create an attachment for an issue.

        Args:
            project: Project ID.
            object_id: Issue ID.
            attached_file: File object to attach.
            description: Optional description for the attachment.
            is_deprecated: Optional flag to mark the attachment as deprecated.

        Returns:
            The newly created attachment detail object, or None if error.
        """
        endpoint = "/issues/attachments"
        data: Dict[str, Union[int, str, bool]] = {
            "project": project, "object_id": object_id}
        if description is not None:
            data["description"] = description
        if is_deprecated is not None:
            data["is_deprecated"] = is_deprecated

        files = {'attached_file': attached_file}
        result = self.client.post(endpoint, data=data, files=files)
        return result if isinstance(result, dict) else None

    def get_attachment(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve details of a specific issue attachment.

        Args:
            attachment_id: The ID of the attachment.

        Returns:
            Attachment detail object, or None if not found/error.
        """
        endpoint = f"/issues/attachments/{attachment_id}"
        result = self.client.get(endpoint)
        return result if isinstance(result, dict) else None

    def edit_attachment(self, attachment_id: int, version: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Edit an issue attachment (partial update).

        Args:
            attachment_id: The ID of the attachment.
            version: The current version number of the attachment.
            data: Dictionary of attributes to update.

        Returns:
            The updated attachment detail object, or None if error.
        """
        endpoint = f"/issues/attachments/{attachment_id}"
        payload = {"version": version}
        payload.update(data)
        result = self.client.patch(endpoint, json=payload)
        return result if isinstance(result, dict) else None

    def update_attachment(self, attachment_id: int, version: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an issue attachment (full update). Use with caution.

        Args:
            attachment_id: The ID of the attachment.
            version: The current version number of the attachment.
            data: Dictionary representing the full attachment object.

        Returns:
            The updated attachment detail object, or None if error.
        """
        endpoint = f"/issues/attachments/{attachment_id}"
        payload = data.copy()
        payload["version"] = version
        result = self.client.put(endpoint, json=payload)
        return result if isinstance(result, dict) else None

    def delete_attachment(self, attachment_id: int) -> Optional[Any]:
        """
        Delete an issue attachment.

        Args:
            attachment_id: The ID of the attachment to delete.

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = f"/issues/attachments/{attachment_id}"
        return self.client.delete(endpoint)
