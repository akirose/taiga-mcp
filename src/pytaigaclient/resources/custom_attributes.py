from typing import Any, Dict, List, Optional, cast

from .base import Resource


class CustomAttributes(Resource):
    """
    Base class for handling Custom Attributes operations in Taiga.

    Custom attributes allow adding custom fields to Taiga entities.
    """

    def __init__(self, client, resource_name):
        """
        Initialize with specific resource name.

        Args:
            client: The Taiga client instance.
            resource_name: The name of the resource (e.g., "userstories", "tasks", "issues", "epics").
        """
        super().__init__(client)
        self.resource_name = resource_name
        self.endpoint = f"/{resource_name}-custom-attributes"
        self.values_endpoint = f"/{resource_name}-custom-attributes-values"

    def list(self, project: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List custom attributes for a resource type.

        Args:
            project: Optional project ID to filter by.

        Returns:
            List of custom attribute detail objects.
        """
        params = {"project": project} if project else None
        result = self.client.get(self.endpoint, params=params)
        return result if isinstance(result, list) else []

    def create(self, project: int, name: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new custom attribute.

        Args:
            project: Project ID.
            name: Name of the custom attribute.
            **kwargs: Other properties (e.g., description, order, type).
                     Supported types: 'text', 'multiline', 'richtext', 'date', 'url', 'checkbox', 'number', 'dropdown'.

        Returns:
            The newly created custom attribute detail object.
        """
        payload = {"project": project, "name": name, **kwargs}
        result = self.client.post(self.endpoint, json=payload)
        return cast(Dict[str, Any], result)

    def get(self, custom_attr_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific custom attribute by its ID.

        Args:
            custom_attr_id: The ID of the custom attribute.

        Returns:
            Custom attribute detail object.
        """
        result = self.client.get(f"{self.endpoint}/{custom_attr_id}")
        return cast(Dict[str, Any], result)

    def edit(self, custom_attr_id: int, **kwargs) -> Dict[str, Any]:
        """
        Edit a custom attribute (partial update).

        Args:
            custom_attr_id: The ID of the custom attribute.
            **kwargs: Fields to update.

        Returns:
            The updated custom attribute detail object.
        """
        result = self.client.patch(
            f"{self.endpoint}/{custom_attr_id}", json=kwargs)
        return cast(Dict[str, Any], result)

    def update(self, custom_attr_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a custom attribute (full update).

        Args:
            custom_attr_id: The ID of the custom attribute.
            data: Complete representation of the custom attribute.

        Returns:
            The updated custom attribute detail object.
        """
        result = self.client.put(
            f"{self.endpoint}/{custom_attr_id}", json=data)
        return cast(Dict[str, Any], result)

    def delete(self, custom_attr_id: int) -> None:
        """
        Delete a custom attribute.

        Args:
            custom_attr_id: The ID of the custom attribute to delete.
        """
        self.client.delete(f"{self.endpoint}/{custom_attr_id}")

    def bulk_update_order(self, project_id: int, bulk_custom_attributes: List[List[int]]) -> None:
        """
        Update the order of multiple custom attributes.

        Args:
            project_id: Project ID.
            bulk_custom_attributes: List of [custom_attr_id, new_order] pairs.
                                   Example: [[1, 10], [2, 5]]
        """
        endpoint = f"{self.endpoint}/bulk_update_order"
        payload = {"project": project_id,
                   f"bulk_{self.resource_name}_custom_attributes": bulk_custom_attributes}
        self.client.post(endpoint, json=payload)

    # Custom attribute values operations

    def get_values(self, entity_id: int) -> Dict[str, Any]:
        """
        Get all custom attribute values for a specific entity.

        Args:
            entity_id: The ID of the entity (user story, task, issue, or epic).

        Returns:
            Object containing all custom attribute values for the entity.
        """
        return cast(Dict[str, Any], self.client.get(f"{self.values_endpoint}/{entity_id}"))

    def update_values(self, entity_id: int, version: int, attributes_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update custom attribute values for an entity.

        Args:
            entity_id: The ID of the entity (user story, task, issue, or epic).
            version: Current version of the entity for optimistic concurrency control.
            attributes_values: Dictionary with attribute values to set.
                             Format: {"attributes_values": {attr_id_1: value1, attr_id_2: value2}}

        Returns:
            Updated custom attribute values object.
        """
        payload = {
            "version": version,
            "attributes_values": attributes_values
        }
        result = self.client.patch(
            f"{self.values_endpoint}/{entity_id}", json=payload)
        return cast(Dict[str, Any], result)


class UserStoryCustomAttributes(CustomAttributes):
    """
    Handles custom attributes for user stories.
    """

    def __init__(self, client):
        super().__init__(client, "userstories")


class TaskCustomAttributes(CustomAttributes):
    """
    Handles custom attributes for tasks.
    """

    def __init__(self, client):
        super().__init__(client, "tasks")


class IssueCustomAttributes(CustomAttributes):
    """
    Handles custom attributes for issues.
    """

    def __init__(self, client):
        super().__init__(client, "issues")


class EpicCustomAttributes(CustomAttributes):
    """
    Handles custom attributes for epics.
    """

    def __init__(self, client):
        super().__init__(client, "epics")
