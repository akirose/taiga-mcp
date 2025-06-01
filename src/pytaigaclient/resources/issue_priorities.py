from typing import Any, Dict, List, Optional

from .base import Resource


class IssuePriorities(Resource):
    """
    Handles operations related to Issue Priorities in Taiga.

    See https://docs.taiga.io/api.html#issue-priorities
    """
    ENDPOINT = "/issue-priorities"

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List issue priorities.

        Args:
            query_params: Dictionary of query parameters (e.g., project).

        Returns:
            List of issue priority detail objects.
        """
        result = self.client.get(self.ENDPOINT, params=query_params)
        return result if isinstance(result, list) else []

    def create(
        self, project: int, name: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue priority.

        Args:
            project: Project ID.
            name: Name of the new priority.
            data: Dictionary containing other attributes (e.g., color, order).

        Returns:
            The newly created issue priority detail object.
        """
        payload = {"project": project, "name": name}
        if data:
            payload.update(data)
        return self.client.post(self.ENDPOINT, json=payload)

    def get(self, priority_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific issue priority by its ID.

        Args:
            priority_id: The ID of the priority.

        Returns:
            Issue priority detail object.
        """
        return self.client.get(f"{self.ENDPOINT}/{priority_id}")

    def edit(self, priority_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit an issue priority (partial update).

        Args:
            priority_id: The ID of the priority.
            data: Dictionary of attributes to update.

        Returns:
            The updated issue priority detail object.
        """
        return self.client.patch(f"{self.ENDPOINT}/{priority_id}", json=data)

    def update(self, priority_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an issue priority (full update). Use with caution.

        Args:
            priority_id: The ID of the priority.
            data: Dictionary representing the full priority object.

        Returns:
            The updated issue priority detail object.
        """
        return self.client.put(f"{self.ENDPOINT}/{priority_id}", json=data)

    def delete(self, priority_id: int) -> Optional[Any]:
        """
        Delete an issue priority.

        Args:
            priority_id: The ID of the priority to delete.

        Returns:
            None if successful (HTTP 204).
        """
        return self.client.delete(f"{self.ENDPOINT}/{priority_id}")

    def bulk_update_order(self, project: int, bulk_issue_priorities: List[List[int]]) -> Optional[Any]:
        """
        Update the order of multiple issue priorities.

        Args:
            project: Project ID.
            bulk_issue_priorities: List of [priority_id, new_order] pairs.
                                   Example: [[1, 10], [2, 5]]

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = f"{self.ENDPOINT}/bulk_update_order"
        payload = {"project": project, "bulk_issue_priorities": bulk_issue_priorities}
        return self.client.post(endpoint, json=payload) 