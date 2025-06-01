from typing import Any, Dict, List, Optional

from .base import Resource


class Tasks(Resource):
    """
    Handles operations related to Tasks in Taiga.

    See https://docs.taiga.io/api.html#tasks
    """

    def list(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List tasks.

        Args:
            query_params: Dictionary of query parameters to filter tasks
                          (e.g., project, status, user_story, milestone, tags).

        Returns:
            List of task detail objects.
        """
        endpoint = "/tasks"
        return self.client.get(endpoint, params=query_params)

    def create(
        self, project: int, subject: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new task.

        Args:
            project: Project ID.
            subject: Task subject.
            data: Dictionary containing other task attributes (e.g., status,
                  milestone, user_story, assigned_to, description, tags, due_date).

        Returns:
            The newly created task detail object.
        """
        endpoint = "/tasks"
        payload = {"project": project, "subject": subject}
        if data:
            payload.update(data)
        return self.client.post(endpoint, json=payload)

    def get(self, task_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific task by its ID.

        Args:
            task_id: The ID of the task.

        Returns:
            Task detail object.
        """
        endpoint = f"/tasks/{task_id}"
        return self.client.get(endpoint)

    def get_by_ref(
        self, ref: int, project: int | str
    ) -> Dict[str, Any]:
        """
        Retrieve details of a task by its reference number and project ID/slug.

        Args:
            ref: The reference number of the task.
            project: The project ID or slug.

        Returns:
            Task detail object.
        """
        endpoint = "/tasks/by_ref"
        query_params = {"ref": ref}
        if isinstance(project, int):
            query_params["project"] = project
        else:
            query_params["project_slug"] = project
        return self.client.get(endpoint, query_params=query_params)

    def edit(self, task_id: int, version: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit a task (partial update).

        Args:
            task_id: The ID of the task.
            version: The current version number of the task for optimistic locking.
            data: Dictionary of attributes to update.

        Returns:
            The updated task detail object.
        """
        endpoint = f"/tasks/{task_id}"
        payload = {"version": version}
        payload.update(data)
        return self.client.patch(endpoint, json=payload)

    def update(self, task_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a task (full update).

        Note: The API documentation primarily shows PATCH for edits.
              A PUT request requires sending the *entire* object. Use with caution.

        Args:
            task_id: The ID of the task.
            data: Dictionary representing the full task object.

        Returns:
            The updated task detail object.
        """
        endpoint = f"/tasks/{task_id}"
        return self.client.put(endpoint, json=data)

    def delete(self, task_id: int) -> None:
        """
        Delete a task.

        Args:
            task_id: The ID of the task to delete.
        """
        endpoint = f"/tasks/{task_id}"
        self.client.delete(endpoint)

    def bulk_create(
        self, project_id: int, bulk_tasks: str, data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create multiple tasks at once.

        Args:
            project_id: Project ID where tasks will be created.
            bulk_tasks: Task subjects, one per line (separated by '\n').
            data: Optional dictionary for additional parameters like milestone_id, us_id, status_id.

        Returns:
            List of newly created task detail objects.
        """
        endpoint = "/tasks/bulk_create"
        payload = {"project_id": project_id, "bulk_tasks": bulk_tasks}
        if data:
            payload.update(data)
        return self.client.post(endpoint, json=payload)

    def filters_data(self, project_id: int) -> Dict[str, Any]:
        """
        Get data for filtering tasks within a project.

        Args:
            project_id: The ID of the project.

        Returns:
            Task filters data object.
        """
        endpoint = "/tasks/filters_data"
        query_params = {"project": project_id}
        return self.client.get(endpoint, query_params=query_params)

    def upvote(self, task_id: int) -> None:
        """
        Vote for a task.

        Args:
            task_id: The ID of the task to vote for.
        """
        endpoint = f"/tasks/{task_id}/upvote"
        self.client.post(endpoint)

    def downvote(self, task_id: int) -> None:
        """
        Remove vote from a task.

        Args:
            task_id: The ID of the task to remove the vote from.
        """
        endpoint = f"/tasks/{task_id}/downvote"
        self.client.post(endpoint)

    def list_voters(self, task_id: int) -> List[Dict[str, Any]]:
        """
        Get the list of voters for a task.

        Args:
            task_id: The ID of the task.

        Returns:
            List of task voter objects.
        """
        endpoint = f"/tasks/{task_id}/voters"
        return self.client.get(endpoint)

    def watch(self, task_id: int) -> None:
        """
        Watch a task.

        Args:
            task_id: The ID of the task to watch.
        """
        endpoint = f"/tasks/{task_id}/watch"
        self.client.post(endpoint)

    def unwatch(self, task_id: int) -> None:
        """
        Stop watching a task.

        Args:
            task_id: The ID of the task to stop watching.
        """
        endpoint = f"/tasks/{task_id}/unwatch"
        self.client.post(endpoint)

    def list_watchers(self, task_id: int) -> List[Dict[str, Any]]:
        """
        Get the list of watchers for a task.

        Args:
            task_id: The ID of the task.

        Returns:
            List of task watcher objects.
        """
        endpoint = f"/tasks/{task_id}/watchers"
        return self.client.get(endpoint)

    # --- Attachment Methods ---

    def list_attachments(self, project: int, object_id: int) -> List[Dict[str, Any]]:
        """
        List attachments for a specific task.

        Args:
            project: Project ID.
            object_id: Task ID.

        Returns:
            List of attachment detail objects.
        """
        endpoint = "/tasks/attachments"
        query_params = {"project": project, "object_id": object_id}
        return self.client.get(endpoint, query_params=query_params)

    def create_attachment(
        self,
        project: int,
        object_id: int,
        file_path: str,
        description: Optional[str] = None,
        is_deprecated: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Create an attachment for a task.

        Args:
            project: Project ID.
            object_id: Task ID.
            file_path: Path to the file to attach.
            description: Optional description for the attachment.
            is_deprecated: Optional flag to mark the attachment as deprecated.

        Returns:
            The newly created attachment detail object.
        """
        endpoint = "/tasks/attachments"
        data = {"project": project, "object_id": object_id}
        if description is not None:
            data["description"] = description
        if is_deprecated is not None:
            data["is_deprecated"] = is_deprecated

        with open(file_path, "rb") as f:
            files = {"attached_file": (file_path.split("/")[-1], f)}
            return self.client.post(endpoint, data=data, files=files, expect_json=True)


    def get_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific task attachment.

        Args:
            attachment_id: The ID of the attachment.

        Returns:
            Attachment detail object.
        """
        endpoint = f"/tasks/attachments/{attachment_id}"
        return self.client.get(endpoint)

    def edit_attachment(
        self, attachment_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Edit a task attachment (partial update).

        Args:
            attachment_id: The ID of the attachment.
            data: Dictionary of attributes to update (e.g., description).

        Returns:
            The updated attachment detail object.
        """
        endpoint = f"/tasks/attachments/{attachment_id}"
        return self.client.patch(endpoint, json=data)

    def update_attachment(
        self, attachment_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a task attachment (full update). Use with caution.

        Args:
            attachment_id: The ID of the attachment.
            data: Dictionary representing the full attachment object.

        Returns:
            The updated attachment detail object.
        """
        endpoint = f"/tasks/attachments/{attachment_id}"
        return self.client.put(endpoint, json=data)

    def delete_attachment(self, attachment_id: int) -> None:
        """
        Delete a task attachment.

        Args:
            attachment_id: The ID of the attachment to delete.
        """
        endpoint = f"/tasks/attachments/{attachment_id}"
        self.client.delete(endpoint)
