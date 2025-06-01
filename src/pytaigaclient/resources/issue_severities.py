from typing import Any, Dict, List, Optional

from .base import Resource


class IssueSeverities(Resource):
    """
    Handles operations related to Issue Severities in Taiga.

    See https://docs.taiga.io/api.html#issue-severities
    """
    ENDPOINT = "/issue-severities"

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List issue severities.

        Args:
            query_params: Dictionary of query parameters (e.g., project).

        Returns:
            List of issue severity detail objects.
        """
        result = self.client.get(self.ENDPOINT, params=query_params)
        return result if isinstance(result, list) else []

    def create(
        self, project: int, name: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue severity.

        Args:
            project: Project ID.
            name: Name of the new severity.
            data: Dictionary containing other attributes (e.g., color, order).

        Returns:
            The newly created issue severity detail object.
        """
        payload = {"project": project, "name": name}
        if data:
            payload.update(data)
        return self.client.post(self.ENDPOINT, json=payload)

    def get(self, severity_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific issue severity by its ID.

        Args:
            severity_id: The ID of the severity.

        Returns:
            Issue severity detail object.
        """
        return self.client.get(f"{self.ENDPOINT}/{severity_id}")

    def edit(self, severity_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit an issue severity (partial update).

        Args:
            severity_id: The ID of the severity.
            data: Dictionary of attributes to update.

        Returns:
            The updated issue severity detail object.
        """
        return self.client.patch(f"{self.ENDPOINT}/{severity_id}", json=data)

    def update(self, severity_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an issue severity (full update). Use with caution.

        Args:
            severity_id: The ID of the severity.
            data: Dictionary representing the full severity object.

        Returns:
            The updated issue severity detail object.
        """
        return self.client.put(f"{self.ENDPOINT}/{severity_id}", json=data)

    def delete(self, severity_id: int) -> Optional[Any]:
        """
        Delete an issue severity.

        Args:
            severity_id: The ID of the severity to delete.

        Returns:
            None if successful (HTTP 204).
        """
        return self.client.delete(f"{self.ENDPOINT}/{severity_id}")

    def bulk_update_order(self, project: int, bulk_issue_severities: List[List[int]]) -> Optional[Any]:
        """
        Update the order of multiple issue severities.

        Args:
            project: Project ID.
            bulk_issue_severities: List of [severity_id, new_order] pairs.
                                     Example: [[1, 10], [2, 5]]

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = f"{self.ENDPOINT}/bulk_update_order"
        payload = {"project": project, "bulk_issue_severities": bulk_issue_severities}
        return self.client.post(endpoint, json=payload) 