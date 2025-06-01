from typing import TYPE_CHECKING, Optional, Dict, Any, List, IO, Union

if TYPE_CHECKING:
    from ..client import TaigaClient


class UserStories:
    """
    Handles User Story related endpoints for the Taiga API.
    """

    def __init__(self, client: 'TaigaClient'):
        """
        Initializes the UserStories resource.

        Args:
            client: The TaigaClient instance.
        """
        self._client = client

    def list(self, **query_params) -> List[Dict[str, Any]]:
        """
        Lists user stories based on query parameters.
        Supports filtering by project, milestone, status, tags, watchers, assigned_to, epic, role, etc.
        Supports exclusion filters like exclude_status, exclude_tags, etc.

        Ref: 18.1. List

        Args:
            **query_params: Arbitrary keyword arguments passed as query parameters.
                            Examples: project=1, milestone=5, status__is_closed=False, tags='frontend,api'

        Returns:
            A list of dictionaries, each representing a user story list object.
        """
        result = self._client.get("/userstories", params=query_params)
        return result if isinstance(result, list) else []

    def list_comments(self, user_story_id: int) -> List[Dict[str, Any]]:
        """
        Lists comments for a specific user story.

        Args:
            user_story_id: The ID of the user story to retrieve comments for.

        Returns:
            A list of dictionaries, each representing a comment on the user story.
        """

        if not isinstance(user_story_id, int):
            raise ValueError("user_story_id must be an integer")

        result = self._client.get(f"/history/userstory/{user_story_id}", params={"type": "comment"})
        return result if isinstance(result, list) else []

    def create(self, project: int, subject: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Creates a new user story.

        Ref: 18.2. Create

        Args:
            project: Project ID (required).
            subject: User story subject/title (required).
            **kwargs: Other optional user story attributes (e.g., assigned_to, milestone,
                      status, description, tags, points, backlog_order, etc.).

        Returns:
            A dictionary representing the newly created user story details, or None if error.
        """
        payload = {"project": project, "subject": subject, **kwargs}
        result = self._client.post("/userstories", json=payload)
        return result if isinstance(result, dict) else None

    def get(self, user_story_id: int) -> Optional[Dict[str, Any]]:
        """
        Gets details of a specific user story by its ID.

        Ref: 18.3. Get

        Args:
            user_story_id: The ID of the user story to retrieve.

        Returns:
            A dictionary representing the user story details, or None if not found/error.
        """
        result = self._client.get(f"/userstories/{user_story_id}")
        return result if isinstance(result, dict) else None

    def get_by_ref(self, ref: int, project: Union[int, str]) -> Optional[Dict[str, Any]]:
        """
        Gets details of a specific user story by its reference number and project ID/slug.

        Ref: 18.4. Get by ref

        Args:
            ref: The reference number of the user story.
            project: The ID or slug of the project.

        Returns:
            A dictionary representing the user story details, or None if not found/error.
        """
        param_key = "project__slug" if isinstance(project, str) else "project"
        params = {"ref": ref, param_key: project}
        result = self._client.get("/userstories/by_ref", params=params)
        return result if isinstance(result, dict) else None

    def edit(self, user_story_id: int, version: int, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Edits a user story (partial update using PATCH).
        Requires the current version for optimistic concurrency control.

        Ref: 18.5. Edit

        Args:
            user_story_id: The ID of the user story to edit.
            version: The current 'version' number of the user story object (for OCC).
            **kwargs: User story attributes to update (e.g., subject, description, status).

        Returns:
            A dictionary representing the updated user story details, or None if error.

        Raises:
            TaigaConcurrencyError: If the provided version does not match the server's version.
        """
        payload = {"version": version, **kwargs}
        result = self._client.patch(f"/userstories/{user_story_id}", json=payload)
        return result if isinstance(result, dict) else None

    def update(self, user_story_id: int, version: int, user_story_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates a user story (full update using PUT).
        Requires the current version and the *complete* user story data structure.
        It's often easier to use `edit()` for partial updates.

        Ref: 18.5. Edit

        Args:
            user_story_id: The ID of the user story to update.
            version: The current 'version' number of the user story object (for OCC).
            user_story_data: A dictionary containing the *full* representation of the user story.

        Returns:
            A dictionary representing the updated user story details, or None if error.

        Raises:
            TaigaConcurrencyError: If the provided version does not match the server's version.
        """
        user_story_data['version'] = version
        result = self._client.put(f"/userstories/{user_story_id}", json=user_story_data)
        return result if isinstance(result, dict) else None

    def delete(self, user_story_id: int) -> Optional[Any]:
        """
        Deletes a user story.

        Ref: 18.6. Delete

        Args:
            user_story_id: The ID of the user story to delete.

        Returns:
            None if successful (HTTP 204), otherwise response data.
        """
        return self._client.delete(f"/userstories/{user_story_id}")

    def bulk_create(self, project_id: int, bulk_stories: str, status_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Creates multiple user stories at once.

        Ref: 18.7. Bulk creation

        Args:
            project_id: The ID of the project to add stories to.
            bulk_stories: A string containing user story subjects, one per line.
            status_id: Optional status ID to assign to all created stories.

        Returns:
            A list of dictionaries representing the newly created user stories.
        """
        payload = {"project_id": project_id, "bulk_stories": bulk_stories}
        if status_id is not None:
            payload["status_id"] = status_id
        result = self._client.post("/userstories/bulk_create", json=payload)
        return result if isinstance(result, list) else []

    def bulk_update_backlog_order(self, project_id: int, bulk_stories: List[Dict[str, int]]) -> List[Dict[str, Any]]:
        """
        Updates the backlog order of multiple user stories.

        Ref: 18.8. Bulk update backlog order

        Args:
            project_id: The project ID.
            bulk_stories: A list of dicts, each with 'us_id' and 'order'.
                          Example: [{'us_id': 1, 'order': 10}, {'us_id': 2, 'order': 15}]

        Returns:
            A list of dictionaries representing the updated user stories.
        """
        payload = {"project_id": project_id, "bulk_stories": bulk_stories}
        result = self._client.post("/userstories/bulk_update_backlog_order", json=payload)
        return result if isinstance(result, list) else []

    def bulk_update_kanban_order(self, project_id: int, bulk_stories: List[Dict[str, int]]) -> List[Dict[str, Any]]:
        """
        Updates the Kanban order of multiple user stories.

        Ref: 18.9. Bulk update kanban order

        Args:
            project_id: The project ID.
            bulk_stories: A list of dicts, each with 'us_id' and 'order'.

        Returns:
            A list of dictionaries representing the updated user stories.
        """
        payload = {"project_id": project_id, "bulk_stories": bulk_stories}
        result = self._client.post("/userstories/bulk_update_kanban_order", json=payload)
        return result if isinstance(result, list) else []

    def bulk_update_sprint_order(self, project_id: int, bulk_stories: List[Dict[str, int]]) -> List[Dict[str, Any]]:
        """
        Updates the sprint (milestone) order of multiple user stories.

        Ref: 18.10. Bulk update sprint order

        Args:
            project_id: The project ID.
            bulk_stories: A list of dicts, each with 'us_id' and 'order'.

        Returns:
            A list of dictionaries representing the updated user stories.
        """
        payload = {"project_id": project_id, "bulk_stories": bulk_stories}
        result = self._client.post("/userstories/bulk_update_sprint_order", json=payload)
        return result if isinstance(result, list) else []

    def bulk_update_milestone(self, project_id: int, milestone_id: int, bulk_stories: List[Dict[str, int]]) -> Optional[Any]:
        """
        Assigns multiple user stories to a milestone and sets their order within it.

        Ref: 18.11. Bulk update milestone

        Args:
            project_id: The project ID.
            milestone_id: The milestone ID to assign stories to.
            bulk_stories: A list of dicts, each with 'us_id' and 'order'.

        Returns:
            None if successful (HTTP 204), otherwise response data.
        """
        payload = {
            "project_id": project_id,
            "milestone_id": milestone_id,
            "bulk_stories": bulk_stories
        }
        return self._client.post("/userstories/bulk_update_milestone", json=payload)

    def filters_data(self, project: int) -> Optional[Dict[str, Any]]:
        """
        Gets data for filtering user stories within a project (e.g., available statuses, tags, members).

        Ref: 18.12. Filters data

        Args:
            project: The project ID.

        Returns:
            A dictionary containing filter data, or None if error.
        """
        result = self._client.get("/userstories/filters_data", params={"project": project})
        return result if isinstance(result, dict) else None

    def upvote(self, user_story_id: int) -> Optional[Any]:
        """
        Adds a vote to a user story for the authenticated user.

        Ref: 18.13. Vote a user story

        Args:
            user_story_id: The ID of the user story to vote for.

        Returns:
            Response data, typically None for successful POST with no body (HTTP 200 OK).
        """
        return self._client.post(f"/userstories/{user_story_id}/upvote")

    def downvote(self, user_story_id: int) -> Optional[Any]:
        """
        Removes a vote from a user story for the authenticated user.

        Ref: 18.14. Remove vote from a user story

        Args:
            user_story_id: The ID of the user story to unvote.

        Returns:
            Response data, typically None for successful POST with no body (HTTP 200 OK).
        """
        return self._client.post(f"/userstories/{user_story_id}/downvote")

    def list_voters(self, user_story_id: int) -> List[Dict[str, Any]]:
        """
        Lists the users who have voted for a specific user story.

        Ref: 18.15. Get user story voters list

        Args:
            user_story_id: The ID of the user story.

        Returns:
            A list of dictionaries, each representing a voter.
        """
        result = self._client.get(f"/userstories/{user_story_id}/voters")
        return result if isinstance(result, list) else []

    def watch(self, user_story_id: int) -> Optional[Any]:
        """
        Starts watching a user story for the authenticated user.

        Ref: 18.16. Watch a user story

        Args:
            user_story_id: The ID of the user story to watch.

        Returns:
            Response data, typically None for successful POST with no body (HTTP 200 OK).
        """
        return self._client.post(f"/userstories/{user_story_id}/watch")

    def unwatch(self, user_story_id: int) -> Optional[Any]:
        """
        Stops watching a user story for the authenticated user.

        Ref: 18.17. Stop watching a user story

        Args:
            user_story_id: The ID of the user story to unwatch.

        Returns:
            Response data, typically None for successful POST with no body (HTTP 200 OK).
        """
        return self._client.post(f"/userstories/{user_story_id}/unwatch")

    def list_watchers(self, user_story_id: int) -> List[Dict[str, Any]]:
        """
        Lists the users who are watching a specific user story.

        Ref: 18.18. List user story watchers

        Args:
            user_story_id: The ID of the user story.

        Returns:
            A list of dictionaries, each representing a watcher.
        """
        # Note: Docs example shows raw user dict, assuming endpoint returns list of watchers
        result = self._client.get(f"/userstories/{user_story_id}/watchers")
        return result if isinstance(result, list) else []

    # Attachment Methods
    def list_attachments(self, project: int, object_id: int) -> List[Dict[str, Any]]:
        """
        Lists attachments for a specific user story.

        Ref: 18.19. List attachments

        Args:
            project: The project ID.
            object_id: The user story ID.

        Returns:
            A list of attachment detail objects.
        """
        params = {"project": project, "object_id": object_id}
        result = self._client.get("/userstories/attachments", params=params)
        return result if isinstance(result, list) else []

    def create_attachment(self, project: int, object_id: int, attached_file: IO, description: Optional[str] = None, is_deprecated: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        """
        Creates a new attachment for a user story.

        Ref: 18.20. Create attachment

        Args:
            project: Project ID (required).
            object_id: User Story ID (required).
            attached_file: File object to upload (required).
            description: Optional description for the attachment.
            is_deprecated: Optional flag to mark the attachment as deprecated.

        Returns:
            A dictionary representing the newly created attachment details, or None if error.
        """
        data = {
            "project": project,
            "object_id": object_id
        }
        if description is not None:
            data["description"] = description
        if is_deprecated is not None:
            data["is_deprecated"] = is_deprecated

        files = {'attached_file': attached_file}

        # Use 'data' for form fields, 'files' for the file upload
        result = self._client.post("/userstories/attachments", data=data, files=files)
        return result if isinstance(result, dict) else None

    def get_attachment(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        """
        Gets details of a specific user story attachment.

        Ref: 18.21. Get attachment

        Args:
            attachment_id: The ID of the attachment.

        Returns:
            A dictionary representing the attachment details, or None if not found/error.
        """
        result = self._client.get(f"/userstories/attachments/{attachment_id}")
        return result if isinstance(result, dict) else None

    def edit_attachment(self, attachment_id: int, version: int, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Edits a user story attachment (partial update using PATCH).

        Ref: 18.22. Edit attachment

        Args:
            attachment_id: The ID of the attachment to edit.
            version: The current 'version' number of the attachment object (for OCC).
            **kwargs: Attachment attributes to update (e.g., description, order, is_deprecated).

        Returns:
            A dictionary representing the updated attachment details, or None if error.
        """
        payload = {"version": version, **kwargs}
        result = self._client.patch(f"/userstories/attachments/{attachment_id}", json=payload)
        return result if isinstance(result, dict) else None

    def update_attachment(self, attachment_id: int, version: int, attachment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates a user story attachment (full update using PUT).

        Ref: 18.22. Edit attachment (implicitly covers PUT)

        Args:
            attachment_id: The ID of the attachment to update.
            version: The current 'version' number of the attachment object (for OCC).
            attachment_data: A dictionary containing the *full* representation of the attachment.

        Returns:
            A dictionary representing the updated attachment details, or None if error.
        """
        attachment_data['version'] = version
        result = self._client.put(f"/userstories/attachments/{attachment_id}", json=attachment_data)
        return result if isinstance(result, dict) else None

    def delete_attachment(self, attachment_id: int) -> Optional[Any]:
        """
        Deletes a user story attachment.

        Ref: 18.23. Delete attachment

        Args:
            attachment_id: The ID of the attachment to delete.

        Returns:
            None if successful (HTTP 204), otherwise response data.
        """
        return self._client.delete(f"/userstories/attachments/{attachment_id}")
