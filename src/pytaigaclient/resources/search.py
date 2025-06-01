from typing import Any, Dict, List, Optional

from .base import Resource


class Search(Resource):
    """
    Handles search operations in Taiga.

    Provides a global search across projects and content types.

    See https://docs.taiga.io/api.html#search
    """

    def search(
        self,
        text: str,
        project: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a global search across Taiga resources.

        Args:
            text: Text to search for.
            project: Optional project ID to limit the search scope.
            **kwargs: Additional search parameters:
                      - exclude_q: Text to exclude.
                      - item_types: List of resource types to include in search.
                      - count: Maximum number of results (default: 100).
                      - order_by: Field to order results by.

        Returns:
            Dictionary with search results organized by item_type.
        """
        endpoint = "/search"
        params = {"text": text, **kwargs}
        if project is not None:
            params["project"] = project

        return self.client.get(endpoint, params=params)

    def user_stories(
        self,
        text: str,
        project: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search specifically for user stories.

        Args:
            text: Text to search for.
            project: Optional project ID to limit the search scope.
            **kwargs: Additional search parameters.

        Returns:
            List of matching user stories.
        """
        params = {"text": text, **kwargs}
        if project is not None:
            params["project"] = project

        result = self.client.get("/search/user_stories", params=params)
        return result if isinstance(result, list) else []

    def tasks(
        self,
        text: str,
        project: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search specifically for tasks.

        Args:
            text: Text to search for.
            project: Optional project ID to limit the search scope.
            **kwargs: Additional search parameters.

        Returns:
            List of matching tasks.
        """
        params = {"text": text, **kwargs}
        if project is not None:
            params["project"] = project

        result = self.client.get("/search/tasks", params=params)
        return result if isinstance(result, list) else []

    def issues(
        self,
        text: str,
        project: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search specifically for issues.

        Args:
            text: Text to search for.
            project: Optional project ID to limit the search scope.
            **kwargs: Additional search parameters.

        Returns:
            List of matching issues.
        """
        params = {"text": text, **kwargs}
        if project is not None:
            params["project"] = project

        result = self.client.get("/search/issues", params=params)
        return result if isinstance(result, list) else []

    def wiki_pages(
        self,
        text: str,
        project: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search specifically for wiki pages.

        Args:
            text: Text to search for.
            project: Optional project ID to limit the search scope.
            **kwargs: Additional search parameters.

        Returns:
            List of matching wiki pages.
        """
        params = {"text": text, **kwargs}
        if project is not None:
            params["project"] = project

        result = self.client.get("/search/wiki_pages", params=params)
        return result if isinstance(result, list) else []

    def epics(
        self,
        text: str,
        project: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search specifically for epics.

        Args:
            text: Text to search for.
            project: Optional project ID to limit the search scope.
            **kwargs: Additional search parameters.

        Returns:
            List of matching epics.
        """
        params = {"text": text, **kwargs}
        if project is not None:
            params["project"] = project

        result = self.client.get("/search/epics", params=params)
        return result if isinstance(result, list) else []
