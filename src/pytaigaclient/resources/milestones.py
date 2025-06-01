from typing import TYPE_CHECKING, Optional, Dict, Any, List

if TYPE_CHECKING:
    # Avoid circular import for type hinting
    from ..client import TaigaClient


class Milestones:
    """
    Handles Milestone (Sprint) related endpoints for the Taiga API.
    """

    def __init__(self, client: 'TaigaClient'):
        """
        Initializes the Milestones resource.

        Args:
            client: The TaigaClient instance.
        """
        self._client = client

    def list(self, project: Optional[int] = None, closed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Lists milestones, optionally filtered by project and closed status.

        Ref: 13.1. List

        Args:
            project: Project ID to filter by.
            closed: Boolean to filter by closed status (True=closed, False=open).

        Returns:
            A list of dictionaries, each representing a milestone detail object.
        """
        params = {}
        if project is not None:
            params["project"] = project
        if closed is not None:
            params["closed"] = closed
        # Type hint expects List[Dict[str, Any]], client.get returns Optional[Union[Dict, List, Any]]
        # Assuming the list endpoint returns a list or raises an error/returns None on failure
        result = self._client.get("/milestones", params=params)
        return result if isinstance(result, list) else []


    def create(self, project: int, name: str, estimated_start: str, estimated_finish: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Creates a new milestone.

        Ref: 13.2. Create

        Args:
            project: Project ID (required).
            name: Milestone name (required).
            estimated_start: Estimated start date in 'YYYY-MM-DD' format (required).
            estimated_finish: Estimated finish date in 'YYYY-MM-DD' format (required).
            **kwargs: Other optional milestone attributes (e.g., disponibility, slug, order, watchers).

        Returns:
            A dictionary representing the newly created milestone details, or None if error.
        """
        payload = {
            "project": project,
            "name": name,
            "estimated_start": estimated_start,
            "estimated_finish": estimated_finish,
            **kwargs
        }
        result = self._client.post("/milestones", json=payload)
        return result if isinstance(result, dict) else None


    def get(self, milestone_id: int) -> Optional[Dict[str, Any]]:
        """
        Gets details of a specific milestone by its ID.

        Ref: 13.3. Get

        Args:
            milestone_id: The ID of the milestone to retrieve.

        Returns:
            A dictionary representing the milestone details, or None if not found/error.
        """
        result = self._client.get(f"/milestones/{milestone_id}")
        return result if isinstance(result, dict) else None

    def edit(self, milestone_id: int, version: int, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Edits a milestone (partial update using PATCH).
        Requires the current version for optimistic concurrency control.

        Ref: 13.4. Edit

        Args:
            milestone_id: The ID of the milestone to edit.
            version: The current 'version' number of the milestone object (for OCC).
            **kwargs: Milestone attributes to update (e.g., name, estimated_start).

        Returns:
            A dictionary representing the updated milestone details, or None if error.

        Raises:
            TaigaConcurrencyError: If the provided version does not match the server's version.
        """
        payload = {"version": version, **kwargs}
        result = self._client.patch(f"/milestones/{milestone_id}", json=payload)
        return result if isinstance(result, dict) else None


    def update(self, milestone_id: int, version: int, milestone_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates a milestone (full update using PUT).
        Requires the current version and the *complete* milestone data structure.
        It's often easier to use `edit()` for partial updates.

        Ref: 13.4. Edit

        Args:
            milestone_id: The ID of the milestone to update.
            version: The current 'version' number of the milestone object (for OCC).
            milestone_data: A dictionary containing the *full* representation of the milestone.

        Returns:
            A dictionary representing the updated milestone details, or None if error.

        Raises:
            TaigaConcurrencyError: If the provided version does not match the server's version.
        """
        # Ensure version is included if not already in milestone_data
        milestone_data['version'] = version
        result = self._client.put(f"/milestones/{milestone_id}", json=milestone_data)
        return result if isinstance(result, dict) else None

    def delete(self, milestone_id: int) -> Optional[Any]:
        """
        Deletes a milestone.

        Ref: 13.5. Delete

        Args:
            milestone_id: The ID of the milestone to delete.

        Returns:
            None if successful (HTTP 204), otherwise response data.
        """
        # delete returns Optional[Union[Dict, List, Any]]
        return self._client.delete(f"/milestones/{milestone_id}")

    def stats(self, milestone_id: int) -> Optional[Dict[str, Any]]:
        """
        Gets statistics for a specific milestone.

        Ref: 13.6. Stats

        Args:
            milestone_id: The ID of the milestone.

        Returns:
            A dictionary containing milestone statistics, or None if error.
        """
        result = self._client.get(f"/milestones/{milestone_id}/stats")
        return result if isinstance(result, dict) else None

    def watch(self, milestone_id: int) -> Optional[Any]:
        """
        Starts watching a milestone for the authenticated user.

        Ref: 13.7. Watch a milestone

        Args:
            milestone_id: The ID of the milestone to watch.

        Returns:
            Response data, typically None for successful POST with no body (HTTP 200 OK).
        """
        return self._client.post(f"/milestones/{milestone_id}/watch")

    def unwatch(self, milestone_id: int) -> Optional[Any]:
        """
        Stops watching a milestone for the authenticated user.

        Ref: 13.8. Stop watching a milestone

        Args:
            milestone_id: The ID of the milestone to unwatch.

        Returns:
            Response data, typically None for successful POST with no body (HTTP 200 OK).
        """
        return self._client.post(f"/milestones/{milestone_id}/unwatch")

    def list_watchers(self, milestone_id: int) -> List[Dict[str, Any]]:
        """
        Lists the users who are watching a specific milestone.

        Ref: 13.9. List milestone watchers

        Args:
            milestone_id: The ID of the milestone.

        Returns:
            A list of dictionaries, each representing a watcher.
        """
        result = self._client.get(f"/milestones/{milestone_id}/watchers")
        return result if isinstance(result, list) else []
