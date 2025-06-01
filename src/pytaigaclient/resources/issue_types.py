from typing import Any, Dict, List, Optional

from .base import Resource


class IssueTypes(Resource):
    """
    Handles operations related to Issue Types in Taiga.

    See https://docs.taiga.io/api.html#issue-types
    """
    ENDPOINT = "/issue-types"

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List issue types.

        Args:
            query_params: Dictionary of query parameters (e.g., project).

        Returns:
            List of issue type detail objects.
        """
        result = self.client.get(self.ENDPOINT, params=query_params)
        return result if isinstance(result, list) else []

    def create(
        self, project: int, name: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue type.

        Args:
            project: Project ID.
            name: Name of the new type.
            data: Dictionary containing other attributes (e.g., color, order).

        Returns:
            The newly created issue type detail object.
        """
        payload = {"project": project, "name": name}
        if data:
            payload.update(data)
        return self.client.post(self.ENDPOINT, json=payload)

    def get(self, type_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific issue type by its ID.

        Args:
            type_id: The ID of the type.

        Returns:
            Issue type detail object.
        """
        return self.client.get(f"{self.ENDPOINT}/{type_id}")

    def edit(self, type_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit an issue type (partial update).

        Args:
            type_id: The ID of the type.
            data: Dictionary of attributes to update.

        Returns:
            The updated issue type detail object.
        """
        return self.client.patch(f"{self.ENDPOINT}/{type_id}", json=data)

    def update(self, type_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an issue type (full update). Use with caution.

        Args:
            type_id: The ID of the type.
            data: Dictionary representing the full type object.

        Returns:
            The updated issue type detail object.
        """
        return self.client.put(f"{self.ENDPOINT}/{type_id}", json=data)

    def delete(self, type_id: int) -> Optional[Any]:
        """
        Delete an issue type.

        Args:
            type_id: The ID of the type to delete.

        Returns:
            None if successful (HTTP 204).
        """
        return self.client.delete(f"{self.ENDPOINT}/{type_id}")

    def bulk_update_order(self, project: int, bulk_issue_types: List[List[int]]) -> Optional[Any]:
        """
        Update the order of multiple issue types.

        Args:
            project: Project ID.
            bulk_issue_types: List of [type_id, new_order] pairs.
                              Example: [[1, 10], [2, 5]]

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = f"{self.ENDPOINT}/bulk_update_order"
        payload = {"project": project, "bulk_issue_types": bulk_issue_types}
        return self.client.post(endpoint, json=payload) 