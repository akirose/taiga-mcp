from typing import Any, Dict, List, Optional

from .base import Resource


class Webhooks(Resource):
    """
    Handles operations related to Webhooks in Taiga.

    Webhooks allow integrating Taiga with external services by sending HTTP
    notifications when events occur in Taiga projects.

    See https://docs.taiga.io/api.html#webhooks
    """
    ENDPOINT = "/webhooks"

    def list(self, project: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List webhooks.

        Args:
            project: Optional project ID to filter by.

        Returns:
            List of webhook detail objects.
        """
        params = {"project": project} if project else None
        result = self.client.get(self.ENDPOINT, params=params)
        return result if isinstance(result, list) else []

    def create(
        self, project: int, name: str, url: str, key: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new webhook.

        Args:
            project: Project ID.
            name: Name for the webhook.
            url: URL that will receive the webhook payload.
            key: Optional secret key for payload signature verification.
            **kwargs: Other optional webhook attributes.

        Returns:
            The newly created webhook detail object.
        """
        payload = {"project": project, "name": name, "url": url, **kwargs}
        if key is not None:
            payload["key"] = key
        return self.client.post(self.ENDPOINT, json=payload)

    def get(self, webhook_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific webhook by its ID.

        Args:
            webhook_id: The ID of the webhook.

        Returns:
            Webhook detail object.
        """
        return self.client.get(f"{self.ENDPOINT}/{webhook_id}")

    def edit(self, webhook_id: int, **kwargs) -> Dict[str, Any]:
        """
        Edit a webhook (partial update).

        Args:
            webhook_id: The ID of the webhook.
            **kwargs: Dictionary of attributes to update.

        Returns:
            The updated webhook detail object.
        """
        return self.client.patch(f"{self.ENDPOINT}/{webhook_id}", json=kwargs)

    def update(self, webhook_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a webhook (full update).

        Args:
            webhook_id: The ID of the webhook.
            data: Dictionary representing the full webhook object.

        Returns:
            The updated webhook detail object.
        """
        return self.client.put(f"{self.ENDPOINT}/{webhook_id}", json=data)

    def delete(self, webhook_id: int) -> None:
        """
        Delete a webhook.

        Args:
            webhook_id: The ID of the webhook to delete.
        """
        self.client.delete(f"{self.ENDPOINT}/{webhook_id}")

    def test(self, webhook_id: int) -> Dict[str, Any]:
        """
        Test a webhook by sending a fake payload.

        Args:
            webhook_id: The ID of the webhook to test.

        Returns:
            Test result object.
        """
        return self.client.post(f"{self.ENDPOINT}/{webhook_id}/test")

    def get_logs(self, webhook_id: int) -> List[Dict[str, Any]]:
        """
        Get the logs of webhook requests.

        Args:
            webhook_id: The ID of the webhook.

        Returns:
            List of webhook log objects.
        """
        result = self.client.get(f"{self.ENDPOINT}/{webhook_id}/logs")
        return result if isinstance(result, list) else []
