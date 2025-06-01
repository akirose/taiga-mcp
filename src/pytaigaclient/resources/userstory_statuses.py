from typing import Any, Dict, List, Optional

from .base import Resource


class UserStoryStatuses(Resource):
    """
    Handles operations related to User Story Statuses in Taiga.

    These define the workflow states for user stories (e.g., New, In Progress, Done).

    See https://docs.taiga.io/api.html#user-story-statuses
    """
    ENDPOINT = "/userstory-statuses"

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List user story statuses.

        Args:
            query_params: Dictionary of query parameters (e.g., project).

        Returns:
            List of user story status detail objects.
        """
        result = self.client.get(self.ENDPOINT, params=query_params)
        return result if isinstance(result, list) else []

    def create(
        self, project: int, name: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new user story status.

        Args:
            project: Project ID.
            name: Name of the new status.
            **kwargs: Dictionary containing other attributes (e.g., color, order, is_closed, is_archived, wip_limit).

        Returns:
            The newly created user story status detail object.
        """
        payload = {"project": project, "name": name, **kwargs}
        return self.client.post(self.ENDPOINT, json=payload)

    def get(self, status_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific user story status by its ID.

        Args:
            status_id: The ID of the status.

        Returns:
            User story status detail object.
        """
        return self.client.get(f"{self.ENDPOINT}/{status_id}")

    def edit(self, status_id: int, **kwargs) -> Dict[str, Any]:
        """
        Edit a user story status (partial update).

        Args:
            status_id: The ID of the status.
            **kwargs: Dictionary of attributes to update.

        Returns:
            The updated user story status detail object.
        """
        return self.client.patch(f"{self.ENDPOINT}/{status_id}", json=kwargs)

    def update(self, status_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a user story status (full update). Use with caution.

        Args:
            status_id: The ID of the status.
            data: Dictionary representing the full status object.

        Returns:
            The updated user story status detail object.
        """
        return self.client.put(f"{self.ENDPOINT}/{status_id}", json=data)

    def delete(self, status_id: int) -> None:
        """
        Delete a user story status.

        Args:
            status_id: The ID of the status to delete.
        """
        self.client.delete(f"{self.ENDPOINT}/{status_id}")

    def bulk_update_order(self, project_id: int, bulk_userstory_statuses: List[List[int]]) -> None:
        """
        Update the order of multiple user story statuses.

        Args:
            project_id: Project ID.
            bulk_userstory_statuses: List of [status_id, new_order] pairs.
                                     Example: [[1, 10], [2, 5]]
        """
        endpoint = f"{self.ENDPOINT}/bulk_update_order"
        payload = {"project": project_id,
                   "bulk_userstory_statuses": bulk_userstory_statuses}
        self.client.post(endpoint, json=payload)
