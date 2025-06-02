# Taiga MCP Server

Taiga MCP is a server that provides an interface to access the [Taiga](https://www.taiga.io/) project management system using the [Model Context Protocol (MCP)](https://github.com/model-context-protocol/model-context-protocol) standard. This allows AI assistants to directly interact with the Taiga API to manage projects, user stories, tasks, and more.

## Key Features

- **Taiga API Integration**: Connect to a Taiga instance and access project data
- **Project Management**: List and filter projects with various criteria
- **User Story Management**: View, filter, and check detailed information of user stories
- **Task Management**: List and retrieve detailed information about tasks
- **Issue Management**: List and retrieve information about issues
- **Reference-based Retrieval**: Find items using their reference numbers within projects

## Installation and Setup

### Requirements

- Python 3.10 or higher
- Access to a Taiga instance

### Installation

```bash
# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

### Environment Configuration

Create a `.env` file with the following content:

```
TAIGA_API_URL=http://your-taiga-instance.com
TAIGA_USERNAME=your-username
TAIGA_PASSWORD=your-password
TAIGA_DEFAULT_PROJECT=your-default-project-id
```

- `TAIGA_API_URL`: Base URL of the Taiga API
- `TAIGA_USERNAME`: Username to log in to Taiga
- `TAIGA_PASSWORD`: Password to log in to Taiga
- `TAIGA_DEFAULT_PROJECT`: (Optional) Default project ID

## Running the Server

```bash
python src/server.py
```

## MCP Tools

The server provides the following MCP tools:

### Project Management

#### `list_projects`

Retrieves a list of Taiga projects with various filtering options.
- Filter by member ID, recruitment status, featured status, backlog/kanban activation

#### `get_project_info`

Retrieves detailed information about a project, including user story statuses.

### User Story Management

#### `list_user_stories`

Lists user stories with various filtering options.
- Filter by project, milestone, status, tags, assignee, and more

#### `get_user_story`

Retrieves detailed information for a specific user story by its ID.
- Includes comments

#### `get_user_story_by_ref`

Retrieves a user story using its reference number within a project.
- Uses the reference number displayed in the Taiga UI (#number)

### Task Management

#### `list_tasks`

Lists tasks with various filtering options.
- Filter by project, milestone, status, tags, assignee, user story, and more

#### `get_task`

Retrieves detailed information for a specific task by its ID.

#### `get_task_by_ref`

Retrieves a task using its reference number within a project.
- Uses the reference number displayed in the Taiga UI (#number)

### Issue Management

#### `list_issues`

Lists issues with various filtering options.
- Filter by project, status, severity, priority, tags, assignee, and more

#### `get_issue`

Retrieves detailed information for a specific issue by its ID.

#### `get_issue_by_ref`

Retrieves an issue using its reference number within a project.
- Uses the reference number displayed in the Taiga UI (#number)

## Development

### Development Mode Installation

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## License

This project is distributed under the MIT License.
