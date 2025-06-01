# taiga_client/resources/projects.py

from typing import TYPE_CHECKING, Optional, Dict, Any, List, IO, Union
import os

from .base import Resource

if TYPE_CHECKING:
    # Avoid circular import for type hinting
    from ..client import TaigaClient


class Projects(Resource):
    """
    Handles project related endpoints for the Taiga API.
    Provides methods for listing, creating, retrieving, updating, deleting projects,
    managing tags, watchers, fans, logos, transfers, templates, and stats.
    """

    def list(self, **query_params) -> List[Dict[str, Any]]:
        """
        Lists projects based on query parameters.
        Supports filtering by member, members, is_looking_for_people, is_featured,
        is_backlog_activated, is_kanban_activated.
        Supports ordering by various fields like memberships__user_order, total_fans, total_activity, etc.

        Ref: 10.1. List

        Args:
            **query_params: Arbitrary keyword arguments passed as query parameters.
                            Examples: member=1, is_featured=True, order_by='total_fans'

        Returns:
            A list of dictionaries, each representing a project list entry.
        """
        return self.client.get("/projects", params=query_params)

    def create(self, name: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Creates a new project.

        Ref: 10.2. Create

        Args:
            name: Project name (required).
            description: Project description (required).
            **kwargs: Other optional project attributes (e.g., creation_template: int,
                      is_private: bool, is_backlog_activated: bool, is_issues_activated: bool,
                      is_kanban_activated: bool, is_wiki_activated: bool,
                      videoconferences: str, videoconferences_extra_data: str).

        Returns:
            A dictionary representing the newly created project details.
        """
        payload = {"name": name, "description": description, **kwargs}
        return self.client.post("/projects", json=payload)

    def get(self, project_id: int) -> Dict[str, Any]:
        """
        Gets details of a specific project by its ID.

        Ref: 10.3. Get

        Args:
            project_id: The ID of the project to retrieve.

        Returns:
            A dictionary representing the project details.
        """
        return self.client.get(f"/projects/{project_id}")

    def get_by_slug(self, slug: str) -> Dict[str, Any]:
        """
        Gets details of a specific project by its slug.

        Ref: 10.4. Get by slug

        Args:
            slug: The slug of the project to retrieve.

        Returns:
            A dictionary representing the project details.
        """
        return self.client.get("/projects/by_slug", params={"slug": slug})

    def edit(self, project_id: int, version: int, **kwargs) -> Dict[str, Any]:
        """
        Edits a project (partial update using PATCH).
        Requires the current version for optimistic concurrency control.

        Ref: 10.5. Edit

        Args:
            project_id: The ID of the project to edit.
            version: The current 'version' number of the project object (for OCC).
            **kwargs: Project attributes to update (e.g., name, description, is_private).

        Returns:
            A dictionary representing the updated project details.

        Raises:
            TaigaConcurrencyError: If the provided version does not match the server's version.
        """
        payload = {"version": version, **kwargs}
        return self.client.patch(f"/projects/{project_id}", json=payload)

    def update(self, project_id: int, version: int, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates a project (full update using PUT).
        Requires the current version and the *complete* project data structure.
        It's often easier to use `edit()` for partial updates.

        Ref: 10.5. Edit

        Args:
            project_id: The ID of the project to update.
            version: The current 'version' number of the project object (for OCC).
            project_data: A dictionary containing the *full* representation of the project.

        Returns:
            A dictionary representing the updated project details.

        Raises:
            TaigaConcurrencyError: If the provided version does not match the server's version.
        """
        # Ensure version is included if not already in project_data
        project_data['version'] = version
        return self.client.put(f"/projects/{project_id}", json=project_data)

    def delete(self, project_id: int) -> None:
        """
        Deletes a project.

        Ref: 10.6. Delete

        Args:
            project_id: The ID of the project to delete.
        """
        self.client.delete(f"/projects/{project_id}")

    def bulk_update_order(self, order_updates: List[Dict[str, Any]]) -> None:
        """
        Updates the display order of multiple projects for the logged-in user.

        Ref: 10.7. Bulk update order

        Args:
            order_updates: A list of dictionaries, where each dictionary contains
                           'project_id' (int) and 'order' (int).
                           Example: [{'project_id': 1, 'order': 10}, {'project_id': 2, 'order': 15}]
        """
        self.client.post("/projects/bulk_update_order", json=order_updates)

    def get_modules_config(self, project_id: int) -> Dict[str, Any]:
        """
        Gets the project modules configuration (e.g., GitHub, GitLab secrets/webhooks).

        Ref: 10.8. Get modules configuration

        Args:
            project_id: The ID of the project.

        Returns:
            A dictionary representing the modules configuration.
        """
        return self.client.get(f"/projects/{project_id}/modules")

    def edit_modules_config(self, project_id: int, **kwargs) -> None:
        """
        Edits the project modules configuration (partial update using PATCH).

        Ref: 10.9. Edit modules configuration

        Args:
            project_id: The ID of the project.
            **kwargs: A dictionary representing the module configurations to update.
                      Example: github={'secret': 'new_secret'}
        """
        self.client.patch(f"/projects/{project_id}/modules", json=kwargs)

    def stats(self, project_id: int) -> Dict[str, Any]:
        """
        Gets project statistics (points, milestones, etc.).

        Ref: 10.10. Stats

        Args:
            project_id: The ID of the project.

        Returns:
            A dictionary containing project statistics.
        """
        return self.client.get(f"/projects/{project_id}/stats")

    def issue_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Gets project issue-specific statistics.

        Ref: 10.11. Issue stats

        Args:
            project_id: The ID of the project.

        Returns:
            A dictionary containing issue statistics.
        """
        return self.client.get(f"/projects/{project_id}/issues_stats")

    def get_tag_colors(self, project_id: int) -> Dict[str, Optional[str]]:
        """
        Gets the defined colors for tags within a project.

        Ref: 10.12. Tag colors

        Args:
            project_id: The ID of the project.

        Returns:
            A dictionary where keys are tag names and values are HEX color strings or None.
        """
        return self.client.get(f"/projects/{project_id}/tags_colors")

    def create_tag(self, project_id: int, tag: str, color: Optional[str] = None) -> None:
        """
        Creates a tag (and optionally assigns a color) within a project.

        Ref: 10.13. Create tag

        Args:
            project_id: The ID of the project.
            tag: The name of the tag to create.
            color: Optional HEX color string (e.g., "#FF0000").
        """
        payload = {"tag": tag, "color": color}
        self.client.post(f"/projects/{project_id}/create_tag", json=payload)

    def edit_tag(self, project_id: int, from_tag: str, to_tag: str, color: Optional[str] = None) -> None:
        """
        Edits a tag within a project (renames and/or changes color).

        Ref: 10.14. Edit tag

        Args:
            project_id: The ID of the project.
            from_tag: The current name of the tag.
            to_tag: The new name for the tag.
            color: Optional new HEX color string. If omitted, color remains unchanged or is removed if set to None.
        """
        payload = {"from_tag": from_tag, "to_tag": to_tag, "color": color}
        self.client.post(f"/projects/{project_id}/edit_tag", json=payload)

    def delete_tag(self, project_id: int, tag: str) -> None:
        """
        Deletes a tag from a project. This removes the tag from all associated items.

        Ref: 10.15. Delete-tag

        Args:
            project_id: The ID of the project.
            tag: The name of the tag to delete.
        """
        payload = {"tag": tag}
        self.client.post(f"/projects/{project_id}/delete_tag", json=payload)

    def mix_tags(self, project_id: int, from_tags: List[str], to_tag: str) -> None:
        """
        Merges multiple tags ('from_tags') into a single tag ('to_tag').
        The 'from_tags' will be removed after merging.

        Ref: 10.16. Mix tags

        Args:
            project_id: The ID of the project.
            from_tags: A list of tag names to merge and remove.
            to_tag: The target tag name.
        """
        payload = {"from_tags": from_tags, "to_tag": to_tag}
        self.client.post(f"/projects/{project_id}/mix_tags", json=payload)

    def like(self, project_id: int) -> None:
        """
        Marks the project as liked by the authenticated user.

        Ref: 10.17. Like a project

        Args:
            project_id: The ID of the project.
        """
        self.client.post(f"/projects/{project_id}/like")

    def unlike(self, project_id: int) -> None:
        """
        Removes the authenticated user's like from the project.

        Ref: 10.18. Unlike a project

        Args:
            project_id: The ID of the project.
        """
        self.client.post(f"/projects/{project_id}/unlike")

    def list_fans(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Lists users who have liked the project.

        Ref: 10.19. List project fans

        Args:
            project_id: The ID of the project.

        Returns:
            A list of dictionaries, each representing a fan (user).
        """
        return self.client.get(f"/projects/{project_id}/fans")

    def watch(self, project_id: int, notify_level: Optional[int] = None) -> None:
        """
        Starts watching the project for the authenticated user.

        Ref: 10.20. Watch a project

        Args:
            project_id: The ID of the project.
            notify_level: Optional notification level (integer, depends on Taiga config).
        """
        payload = {}
        if notify_level is not None:
            payload["notify_level"] = notify_level
        self.client.post(
            f"/projects/{project_id}/watch", json=payload if payload else None)

    def unwatch(self, project_id: int) -> None:
        """
        Stops watching the project for the authenticated user.

        Ref: 10.21. Stop watching project

        Args:
            project_id: The ID of the project.
        """
        self.client.post(f"/projects/{project_id}/unwatch")

    def list_watchers(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Lists users who are watching the project.

        Ref: 10.22. List project watchers

        Args:
            project_id: The ID of the project.

        Returns:
            A list of dictionaries, each representing a watcher (user).
        """
        return self.client.get(f"/projects/{project_id}/watchers")

    def create_template_from_project(self, project_id: int, template_name: str, template_description: str) -> Dict[str, Any]:
        """
        Creates a new project template based on an existing project's settings.
        Requires admin privileges.

        Ref: 10.23. Create template

        Args:
            project_id: The ID of the source project.
            template_name: The name for the new template.
            template_description: The description for the new template.

        Returns:
            A dictionary representing the newly created project template.
        """
        payload = {"template_name": template_name,
                   "template_description": template_description}
        return self.client.post(f"/projects/{project_id}/create_template", json=payload)

    def leave(self, project_id: int) -> None:
        """
        Removes the authenticated user from the project membership.
        Cannot be used by the project owner.

        Ref: 10.24. Leave

        Args:
            project_id: The ID of the project to leave.
        """
        self.client.post(f"/projects/{project_id}/leave")

    def change_logo(self, project_id: int, logo_file: Union[str, IO]) -> Dict[str, Any]:
        """
        Uploads and sets a new logo for the project.

        Ref: 10.25. Change logo

        Args:
            project_id: The ID of the project.
            logo_file: Path to the logo file (string) or a file-like object.

        Returns:
            A dictionary representing the updated project details (including new logo URLs).
        """
        if isinstance(logo_file, str):
            file_path = logo_file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Logo file not found at: {file_path}")
            # It's crucial to open in binary mode 'rb'
            with open(file_path, 'rb') as f:
                # Define filename for the multipart request part
                files = {'logo': (os.path.basename(file_path), f)}
                return self.client.post(f"/projects/{project_id}/change_logo", files=files)
        else:
            # Assume it's an already opened file-like object (opened in binary mode)
            # You might need to determine a filename if the API requires it
            files = {'logo': ('uploaded_logo', logo_file)
                     }  # Use a generic filename
            return self.client.post(f"/projects/{project_id}/change_logo", files=files)

    def remove_logo(self, project_id: int) -> Dict[str, Any]:
        """
        Removes the current logo from the project.

        Ref: 10.26. Remove logo

        Args:
            project_id: The ID of the project.

        Returns:
            A dictionary representing the updated project details (with logo URLs set to null).
        """
        return self.client.post(f"/projects/{project_id}/remove_logo")

    def transfer_validate_token(self, project_id: int, token: str) -> None:
        """
        Validates if a project transfer token is valid for the authenticated user.

        Ref: 10.27. Transfer validate-token

        Args:
            project_id: The ID of the project related to the token.
            token: The transfer token received (usually via email).
        """
        payload = {"token": token}
        self.client.post(
            f"/projects/{project_id}/transfer_validate_token", json=payload)

    def transfer_request(self, project_id: int) -> None:
        """
        Sends a request to the project owner to initiate a transfer to the authenticated user.
        (Note: Documentation is slightly ambiguous; this might be intended for non-owners requesting ownership).

        Ref: 10.28. Transfer request

        Args:
            project_id: The ID of the project to request transfer for.
        """
        self.client.post(f"/projects/{project_id}/transfer_request")

    def transfer_start(self, project_id: int, user_id: int) -> None:
        """
        Initiates the transfer process of a project owned by the authenticated user to another admin member.
        Sends an email with a transfer token to the target user.

        Ref: 10.29. Transfer start

        Args:
            project_id: The ID of the project to transfer.
            user_id: The ID of the target admin user to transfer ownership to.
        """
        payload = {"user": user_id}
        self.client.post(
            f"/projects/{project_id}/transfer_start", json=payload)

    def transfer_accept(self, project_id: int, token: str, reason: Optional[str] = None) -> None:
        """
        Accepts the transfer of a project using the received transfer token.
        The authenticated user becomes the new owner.

        Ref: 10.30. Transfer accept

        Args:
            project_id: The ID of the project being transferred.
            token: The transfer token received via email.
            reason: Optional reason included in the email response to the original owner.
        """
        payload = {"token": token, "reason": reason}
        self.client.post(
            f"/projects/{project_id}/transfer_accept", json=payload)

    def transfer_reject(self, project_id: int, token: str, reason: Optional[str] = None) -> None:
        """
        Rejects the transfer of a project using the received transfer token.

        Ref: 10.31. Transfer reject

        Args:
            project_id: The ID of the project transfer being rejected.
            token: The transfer token received via email.
            reason: Optional reason included in the email response to the original owner.
        """
        payload = {"token": token, "reason": reason}
        self.client.post(
            f"/projects/{project_id}/transfer_reject", json=payload)

    def duplicate(self, project_id: int, name: str, description: str, is_private: bool, users: Optional[List[Dict[str, int]]] = None) -> Dict[str, Any]:
        """
        Creates a duplicate of an existing project with specified settings.

        Ref: 10.32. Duplicate

        Args:
            project_id: The ID of the project to duplicate.
            name: The name for the new duplicated project.
            description: The description for the new duplicated project.
            is_private: Whether the new project should be private.
            users: Optional list of user IDs to add as members to the new project.
                   Example: [{'id': 8}, {'id': 10}]

        Returns:
            A dictionary representing the newly created duplicated project.
        """
        payload = {
            "name": name,
            "description": description,
            "is_private": is_private,
        }
        if users is not None:
            payload["users"] = users  # Add only if provided
        return self.client.post(f"/projects/{project_id}/duplicate", json=payload)
