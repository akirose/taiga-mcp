from typing import Any, Dict, List, Optional, Union, IO

from .base import Resource


class Epics(Resource):
    """
    Handles operations related to Epics in Taiga.

    Epics are large user stories that can be broken down into smaller stories.
    They help organize and track large features or initiatives.

    See https://docs.taiga.io/api.html#epics
    """

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List epics with optional filtering.

        Args:
            query_params: Dictionary of query parameters to filter epics
                          (e.g., project, status, assigned_to, owner, tags).

        Returns:
            List of epic detail objects.
        """
        endpoint = "/epics"
        result = self.client.get(endpoint, params=query_params)
        return result if isinstance(result, list) else []

    def create(self, project: int, subject: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new epic.

        Args:
            project: Project ID.
            subject: Epic subject/title.
            **kwargs: Other optional epic attributes (e.g., assigned_to,
                      status, description, tags, blocked_note, client_requirement,
                      team_requirement, epics_order).

        Returns:
            The newly created epic detail object.
        """
        endpoint = "/epics"
        payload = {"project": project, "subject": subject, **kwargs}
        return self.client.post(endpoint, json=payload)

    def get(self, epic_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific epic by its ID.

        Args:
            epic_id: The ID of the epic.

        Returns:
            Epic detail object.
        """
        endpoint = f"/epics/{epic_id}"
        return self.client.get(endpoint)

    def get_by_ref(self, ref: int, project: Union[int, str]) -> Dict[str, Any]:
        """
        Retrieve details of an epic by its reference number and project ID/slug.

        Args:
            ref: The reference number of the epic.
            project: The project ID or slug.

        Returns:
            Epic detail object.
        """
        endpoint = "/epics/by_ref"
        query_params = {"ref": ref}
        if isinstance(project, int):
            query_params["project"] = project
        else:
            query_params["project__slug"] = project
        return self.client.get(endpoint, params=query_params)

    def edit(self, epic_id: int, version: int, **kwargs) -> Dict[str, Any]:
        """
        Edit an epic (partial update).

        Args:
            epic_id: The ID of the epic.
            version: The current version number of the epic for optimistic locking.
            **kwargs: Dictionary of attributes to update.

        Returns:
            The updated epic detail object.
        """
        endpoint = f"/epics/{epic_id}"
        payload = {"version": version, **kwargs}
        return self.client.patch(endpoint, json=payload)

    def update(self, epic_id: int, version: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an epic (full update).

        Args:
            epic_id: The ID of the epic.
            version: The current version number of the epic for optimistic locking.
            data: Dictionary representing the full epic object.

        Returns:
            The updated epic detail object.
        """
        endpoint = f"/epics/{epic_id}"
        data = data.copy()
        data["version"] = version
        return self.client.put(endpoint, json=data)

    def delete(self, epic_id: int) -> None:
        """
        Delete an epic.

        Args:
            epic_id: The ID of the epic to delete.
        """
        endpoint = f"/epics/{epic_id}"
        self.client.delete(endpoint)

    def filters_data(self, project_id: int) -> Dict[str, Any]:
        """
        Get data for filtering epics within a project.

        Args:
            project_id: The ID of the project.

        Returns:
            Epic filters data object.
        """
        endpoint = "/epics/filters_data"
        query_params = {"project": project_id}
        return self.client.get(endpoint, params=query_params)

    def upvote(self, epic_id: int) -> None:
        """
        Vote for an epic.

        Args:
            epic_id: The ID of the epic to vote for.
        """
        endpoint = f"/epics/{epic_id}/upvote"
        self.client.post(endpoint)

    def downvote(self, epic_id: int) -> None:
        """
        Remove vote from an epic.

        Args:
            epic_id: The ID of the epic to remove the vote from.
        """
        endpoint = f"/epics/{epic_id}/downvote"
        self.client.post(endpoint)

    def list_voters(self, epic_id: int) -> List[Dict[str, Any]]:
        """
        Get the list of voters for an epic.

        Args:
            epic_id: The ID of the epic.

        Returns:
            List of epic voter objects.
        """
        endpoint = f"/epics/{epic_id}/voters"
        result = self.client.get(endpoint)
        return result if isinstance(result, list) else []

    def watch(self, epic_id: int) -> None:
        """
        Watch an epic.

        Args:
            epic_id: The ID of the epic to watch.
        """
        endpoint = f"/epics/{epic_id}/watch"
        self.client.post(endpoint)

    def unwatch(self, epic_id: int) -> None:
        """
        Stop watching an epic.

        Args:
            epic_id: The ID of the epic to stop watching.
        """
        endpoint = f"/epics/{epic_id}/unwatch"
        self.client.post(endpoint)

    def list_watchers(self, epic_id: int) -> List[Dict[str, Any]]:
        """
        Get the list of watchers for an epic.

        Args:
            epic_id: The ID of the epic.

        Returns:
            List of epic watcher objects.
        """
        endpoint = f"/epics/{epic_id}/watchers"
        result = self.client.get(endpoint)
        return result if isinstance(result, list) else []

    def list_related_user_stories(self, epic_id: int) -> List[Dict[str, Any]]:
        """
        Get the list of user stories related to an epic.

        Args:
            epic_id: The ID of the epic.

        Returns:
            List of related user stories.
        """
        endpoint = f"/epics/{epic_id}/related_userstories"
        result = self.client.get(endpoint)
        return result if isinstance(result, list) else []

    def add_related_user_story(self, epic_id: int, user_story_id: int, **kwargs) -> Dict[str, Any]:
        """
        Add a user story to an epic.

        Args:
            epic_id: The ID of the epic.
            user_story_id: The ID of the user story to relate.
            **kwargs: Other optional attributes (e.g., order).

        Returns:
            The newly created epic-user story relationship.
        """
        endpoint = f"/epics/{epic_id}/related_userstories"
        payload = {"user_story": user_story_id, **kwargs}
        return self.client.post(endpoint, json=payload)

    def edit_related_user_story(self, epic_id: int, user_story_id: int, **kwargs) -> Dict[str, Any]:
        """
        Edit an existing relationship between an epic and a user story.

        Args:
            epic_id: The ID of the epic.
            user_story_id: The ID of the related user story.
            **kwargs: Attributes to update (e.g., order).

        Returns:
            The updated relationship.
        """
        endpoint = f"/epics/{epic_id}/related_userstories/{user_story_id}"
        return self.client.patch(endpoint, json=kwargs)

    def delete_related_user_story(self, epic_id: int, user_story_id: int) -> None:
        """
        Remove a user story from an epic.

        Args:
            epic_id: The ID of the epic.
            user_story_id: The ID of the user story to remove.
        """
        endpoint = f"/epics/{epic_id}/related_userstories/{user_story_id}"
        self.client.delete(endpoint)

    def bulk_create_related_user_stories(
        self, epic_id: int, user_story_ids: List[int], **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Relate multiple user stories to an epic at once.

        Args:
            epic_id: The ID of the epic.
            user_story_ids: List of user story IDs to relate.
            **kwargs: Other optional attributes.

        Returns:
            List of newly created relationships.
        """
        endpoint = f"/epics/{epic_id}/related_userstories/bulk_create"
        payload = {"bulk_userstories": user_story_ids, **kwargs}
        result = self.client.post(endpoint, json=payload)
        return result if isinstance(result, list) else []

    # --- Attachment Methods ---

    def list_attachments(self, project_id: int, epic_id: int) -> List[Dict[str, Any]]:
        """
        List attachments for a specific epic.

        Args:
            project_id: Project ID.
            epic_id: Epic ID.

        Returns:
            List of attachment detail objects.
        """
        endpoint = "/epics/attachments"
        query_params = {"project": project_id, "object_id": epic_id}
        result = self.client.get(endpoint, params=query_params)
        return result if isinstance(result, list) else []

    def create_attachment(
        self, project_id: int, epic_id: int, attached_file: IO,
        description: Optional[str] = None, is_deprecated: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Create an attachment for an epic.

        Args:
            project_id: Project ID.
            epic_id: Epic ID.
            attached_file: File-like object to attach.
            description: Optional description for the attachment.
            is_deprecated: Optional flag to mark the attachment as deprecated.

        Returns:
            The newly created attachment detail object.
        """
        endpoint = "/epics/attachments"
        data = {"project": project_id, "object_id": epic_id}
        if description is not None:
            data["description"] = description
        if is_deprecated is not None:
            data["is_deprecated"] = is_deprecated

        files = {"attached_file": attached_file}
        return self.client.post(endpoint, data=data, files=files)

    def get_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific epic attachment.

        Args:
            attachment_id: The ID of the attachment.

        Returns:
            Attachment detail object.
        """
        endpoint = f"/epics/attachments/{attachment_id}"
        return self.client.get(endpoint)

    def edit_attachment(
        self, attachment_id: int, version: int, **kwargs
    ) -> Dict[str, Any]:
        """
        Edit an epic attachment (partial update).

        Args:
            attachment_id: The ID of the attachment.
            version: The current version number of the attachment.
            **kwargs: Dictionary of attributes to update (e.g., description).

        Returns:
            The updated attachment detail object.
        """
        endpoint = f"/epics/attachments/{attachment_id}"
        payload = {"version": version, **kwargs}
        return self.client.patch(endpoint, json=payload)

    def update_attachment(
        self, attachment_id: int, version: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an epic attachment (full update).

        Args:
            attachment_id: The ID of the attachment.
            version: The current version number of the attachment.
            data: Dictionary representing the full attachment object.

        Returns:
            The updated attachment detail object.
        """
        endpoint = f"/epics/attachments/{attachment_id}"
        data = data.copy()
        data["version"] = version
        return self.client.put(endpoint, json=data)

    def delete_attachment(self, attachment_id: int) -> None:
        """
        Delete an epic attachment.

        Args:
            attachment_id: The ID of the attachment to delete.
        """
        endpoint = f"/epics/attachments/{attachment_id}"
        self.client.delete(endpoint)
