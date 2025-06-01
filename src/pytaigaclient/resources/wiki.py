from typing import Any, Dict, List, Optional, Union, IO

from .base import Resource


class Wiki(Resource):
    """
    Handles operations related to Wiki Pages in Taiga.

    See https://docs.taiga.io/api.html#wiki-pages
    """

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List wiki pages.

        Args:
            query_params: Dictionary of query parameters (e.g., project).

        Returns:
            List of wiki page detail objects.
        """
        endpoint = "/wiki"
        result = self.client.get(endpoint, params=query_params)
        return result if isinstance(result, list) else []

    def create(
        self, project: int, slug: str, content: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new wiki page.

        Args:
            project: Project ID.
            slug: Unique slug for the page URL.
            content: Page content (in Markdown or the configured format).
            data: Dictionary containing other attributes (e.g., watchers).

        Returns:
            The newly created wiki page detail object.
        """
        endpoint = "/wiki"
        payload = {"project": project, "slug": slug, "content": content}
        if data:
            payload.update(data)
        result = self.client.post(endpoint, json=payload)
        return result if isinstance(result, dict) else {}

    def get(self, wiki_page_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific wiki page by its ID.

        Args:
            wiki_page_id: The ID of the wiki page.

        Returns:
            Wiki page detail object.
        """
        endpoint = f"/wiki/{wiki_page_id}"
        result = self.client.get(endpoint)
        return result if isinstance(result, dict) else {}

    def get_by_slug(
        self, slug: str, project: int
    ) -> Dict[str, Any]:
        """
        Retrieve details of a wiki page by its slug and project ID.

        Args:
            slug: The slug of the wiki page.
            project: The project ID.

        Returns:
            Wiki page detail object.
        """
        endpoint = "/wiki/by_slug"
        params = {"slug": slug, "project": project}
        result = self.client.get(endpoint, params=params)
        return result if isinstance(result, dict) else {}

    def edit(self, wiki_page_id: int, version: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit a wiki page (partial update).

        Args:
            wiki_page_id: The ID of the wiki page.
            version: The current version number of the page for optimistic locking.
            data: Dictionary of attributes to update (e.g., content, slug).

        Returns:
            The updated wiki page detail object.
        """
        endpoint = f"/wiki/{wiki_page_id}"
        payload = {"version": version}
        payload.update(data)
        result = self.client.patch(endpoint, json=payload)
        return result if isinstance(result, dict) else {}

    def update(self, wiki_page_id: int, version: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a wiki page (full update). Use with caution.

        Args:
            wiki_page_id: The ID of the wiki page.
            version: The current version number of the page.
            data: Dictionary representing the full wiki page object.

        Returns:
            The updated wiki page detail object.
        """
        endpoint = f"/wiki/{wiki_page_id}"
        payload = data.copy()
        payload["version"] = version
        result = self.client.put(endpoint, json=payload)
        return result if isinstance(result, dict) else {}

    def delete(self, wiki_page_id: int) -> Optional[Any]:
        """
        Delete a wiki page.

        Args:
            wiki_page_id: The ID of the wiki page to delete.

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = f"/wiki/{wiki_page_id}"
        return self.client.delete(endpoint)

    def watch(self, wiki_page_id: int) -> Optional[Any]:
        """
        Watch a wiki page.

        Args:
            wiki_page_id: The ID of the wiki page to watch.

        Returns:
            None if successful (HTTP 200 OK with empty body).
        """
        endpoint = f"/wiki/{wiki_page_id}/watch"
        return self.client.post(endpoint)

    def unwatch(self, wiki_page_id: int) -> Optional[Any]:
        """
        Stop watching a wiki page.

        Args:
            wiki_page_id: The ID of the wiki page to stop watching.

        Returns:
            None if successful (HTTP 200 OK with empty body).
        """
        endpoint = f"/wiki/{wiki_page_id}/unwatch"
        return self.client.post(endpoint)

    def list_watchers(self, wiki_page_id: int) -> List[Dict[str, Any]]:
        """
        Get the list of watchers for a wiki page.

        Args:
            wiki_page_id: The ID of the wiki page.

        Returns:
            List of wiki page watcher objects.
        """
        endpoint = f"/wiki/{wiki_page_id}/watchers"
        result = self.client.get(endpoint)
        return result if isinstance(result, list) else []

    # --- Attachment Methods ---

    def list_attachments(self, project: int, object_id: int) -> List[Dict[str, Any]]:
        """
        List attachments for a specific wiki page.

        Args:
            project: Project ID.
            object_id: Wiki page ID.

        Returns:
            List of attachment detail objects.
        """
        endpoint = "/wiki/attachments"
        params = {"project": project, "object_id": object_id}
        result = self.client.get(endpoint, params=params)
        return result if isinstance(result, list) else []

    def create_attachment(
        self, project: int, object_id: int, attached_file: IO, description: Optional[str] = None, is_deprecated: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create an attachment for a wiki page.

        Args:
            project: Project ID.
            object_id: Wiki page ID.
            attached_file: File object to attach.
            description: Optional description for the attachment.
            is_deprecated: Optional flag to mark the attachment as deprecated.

        Returns:
            The newly created attachment detail object, or None if error.
        """
        endpoint = "/wiki/attachments"
        data: Dict[str, Any] = {"project": project, "object_id": object_id}
        if description is not None:
            data["description"] = description
        if is_deprecated is not None:
            data["is_deprecated"] = is_deprecated

        files = {'attached_file': attached_file}
        result = self.client.post(endpoint, data=data, files=files)
        return result if isinstance(result, dict) else None

    def get_attachment(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve details of a specific wiki page attachment.

        Args:
            attachment_id: The ID of the attachment.

        Returns:
            Attachment detail object, or None if not found/error.
        """
        endpoint = f"/wiki/attachments/{attachment_id}"
        result = self.client.get(endpoint)
        return result if isinstance(result, dict) else None

    def edit_attachment(self, attachment_id: int, version: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Edit a wiki page attachment (partial update).

        Args:
            attachment_id: The ID of the attachment.
            version: The current version number of the attachment.
            data: Dictionary of attributes to update.

        Returns:
            The updated attachment detail object, or None if error.
        """
        endpoint = f"/wiki/attachments/{attachment_id}"
        payload = {"version": version}
        payload.update(data)
        result = self.client.patch(endpoint, json=payload)
        return result if isinstance(result, dict) else None

    def update_attachment(self, attachment_id: int, version: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a wiki page attachment (full update). Use with caution.

        Args:
            attachment_id: The ID of the attachment.
            version: The current version number of the attachment.
            data: Dictionary representing the full attachment object.

        Returns:
            The updated attachment detail object, or None if error.
        """
        endpoint = f"/wiki/attachments/{attachment_id}"
        payload = data.copy()
        payload["version"] = version
        result = self.client.put(endpoint, json=payload)
        return result if isinstance(result, dict) else None

    def delete_attachment(self, attachment_id: int) -> Optional[Any]:
        """
        Delete a wiki page attachment.

        Args:
            attachment_id: The ID of the attachment to delete.

        Returns:
            None if successful (HTTP 204).
        """
        endpoint = f"/wiki/attachments/{attachment_id}"
        return self.client.delete(endpoint)
