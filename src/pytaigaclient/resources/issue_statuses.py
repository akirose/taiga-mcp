from typing import Any, Dict, List, Optional

from .base import Resource


class IssueStatuses(Resource):
    """
    Handles operations related to Issue Statuses in Taiga.

    See https://docs.taiga.io/api.html#issue-status
    """
    ENDPOINT = "/issue-statuses"

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List issue statuses.

        Args:
            query_params: Dictionary of query parameters (e.g., project).

        Returns:
            List of issue status detail objects.
        """
        result = self.client.get(self.ENDPOINT, params=query_params)
        return result if isinstance(result, list) else []

    def create(
        self, project: int, name: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue status.

        Args:
            project: Project ID.
            name: Name of the new status.
            data: Dictionary containing other attributes (e.g., color, is_closed, order).

        Returns:
            The newly created issue status detail object.
        """
        payload = {"project": project, "name": name}
        if data:
            payload.update(data)
        return self.client.post(self.ENDPOINT, json=payload)

    def get(self, status_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific issue status by its ID.

        Args:
            status_id: The ID of the status.

        Returns:
            Issue status detail object.
        """
        return self.client.get(f"{self.ENDPOINT}/{status_id}")

    def edit(self, status_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit an issue status (partial update).

        Args:
            status_id: The ID of the status.
            data: Dictionary of attributes to update.

        Returns:
            The updated issue status detail object.
        """
        return self.client.patch(f"{self.ENDPOINT}/{status_id}", json=data)

    def update(self, status_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an issue status (full update). Use with caution.

        Args:
            status_id: The ID of the status.
            data: Dictionary representing the full status object.

        Returns:
            The updated issue status detail object.
        """
        return self.client.put(f"{self.ENDPOINT}/{status_id}", json=data)

    def delete(self, status_id: int) -> Optional[Any]:
        """
        Delete an issue status.

        Args:
            status_id: The ID of the status to delete.

        Returns:
            None if successful (HTTP 204).
        """
        return self.client.delete(f"{self.ENDPOINT}/{status_id}")

    def bulk_update_order(self, project: int, bulk_issue_statuses: List[List[int]]) -> Optional[Any]:
        """
        Update the order of multiple issue statuses.

        Args:
            project: Project ID.
            bulk_issue_statuses: List of [status_id, new_order] pairs.
                                Example: [[1, 10], [2, 5]]

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = f"{self.ENDPOINT}/bulk_update_order"
        payload = {"project": project, "bulk_issue_statuses": bulk_issue_statuses}
        return self.client.post(endpoint, json=payload) 