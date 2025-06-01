from typing import Any, Dict, List, Optional

from .base import Resource


class Points(Resource):
    """
    Handles operations related to Points in Taiga.

    Points are used for estimating user stories using different scales
    (e.g., Fibonacci, linear, etc.).

    See https://docs.taiga.io/api.html#points
    """
    ENDPOINT = "/points"

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List points.

        Args:
            query_params: Dictionary of query parameters (e.g., project).

        Returns:
            List of points detail objects.
        """
        result = self.client.get(self.ENDPOINT, params=query_params)
        return result if isinstance(result, list) else []

    def create(
        self, project: int, name: str, value: Optional[float] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new point estimate value.

        Args:
            project: Project ID.
            name: Name of the point value (e.g., "1", "2", "3", "5", "8", "13", "?").
            value: Numeric value for the point (can be null for special values like "?").
            **kwargs: Dictionary containing other attributes (e.g., order).

        Returns:
            The newly created points detail object.
        """
        payload = {"project": project, "name": name, **kwargs}
        if value is not None:
            payload["value"] = value
        return self.client.post(self.ENDPOINT, json=payload)

    def get(self, points_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific points value by its ID.

        Args:
            points_id: The ID of the points.

        Returns:
            Points detail object.
        """
        return self.client.get(f"{self.ENDPOINT}/{points_id}")

    def edit(self, points_id: int, **kwargs) -> Dict[str, Any]:
        """
        Edit a points value (partial update).

        Args:
            points_id: The ID of the points.
            **kwargs: Dictionary of attributes to update.

        Returns:
            The updated points detail object.
        """
        return self.client.patch(f"{self.ENDPOINT}/{points_id}", json=kwargs)

    def update(self, points_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a points value (full update). Use with caution.

        Args:
            points_id: The ID of the points.
            data: Dictionary representing the full points object.

        Returns:
            The updated points detail object.
        """
        return self.client.put(f"{self.ENDPOINT}/{points_id}", json=data)

    def delete(self, points_id: int) -> None:
        """
        Delete a points value.

        Args:
            points_id: The ID of the points value to delete.
        """
        self.client.delete(f"{self.ENDPOINT}/{points_id}")

    def bulk_update_order(self, project_id: int, bulk_points: List[List[int]]) -> None:
        """
        Update the order of multiple point values.

        Args:
            project_id: Project ID.
            bulk_points: List of [points_id, new_order] pairs.
                        Example: [[1, 10], [2, 5]]
        """
        endpoint = f"{self.ENDPOINT}/bulk_update_order"
        payload = {"project": project_id, "bulk_points": bulk_points}
        self.client.post(endpoint, json=payload)
