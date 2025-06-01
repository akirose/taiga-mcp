from typing import Any, Dict, List, Optional

from .base import Resource


class Timeline(Resource):
    """
    Handles timeline/activity related operations in Taiga.

    The timeline shows activity across projects and users.

    See https://docs.taiga.io/api.html#timeline
    """

    def user_timeline(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get timeline entries for the authenticated user.
        Shows activity in projects the user is involved in.

        Args:
            page: Optional page number for pagination.
            page_size: Optional page size for pagination.

        Returns:
            List of timeline entries.
        """
        endpoint = "/timeline"
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size

        result = self.client.get(endpoint, params=params)
        return result if isinstance(result, list) else []

    def user_timeline_detail(
        self,
        user_id: int,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get timeline entries for a specific user.

        Args:
            user_id: The ID of the user.
            page: Optional page number for pagination.
            page_size: Optional page size for pagination.

        Returns:
            List of timeline entries for the user.
        """
        endpoint = f"/timeline/user/{user_id}"
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size

        result = self.client.get(endpoint, params=params)
        return result if isinstance(result, list) else []

    def project_timeline(
        self,
        project_id: int,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get timeline entries for a specific project.

        Args:
            project_id: The ID of the project.
            page: Optional page number for pagination.
            page_size: Optional page size for pagination.

        Returns:
            List of timeline entries for the project.
        """
        endpoint = f"/timeline/project/{project_id}"
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size

        result = self.client.get(endpoint, params=params)
        return result if isinstance(result, list) else []
