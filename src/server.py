import logging
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
from pytaigaclient import TaigaClient  # Import the new client
# Assuming pytaigaclient also has a base exception
from pytaigaclient.exceptions import TaigaException, TaigaAuthenticationError

# --- Load environment variables ---
load_dotenv()  # .env 파일이 있으면 로드합니다

# --- Logging Setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log to stderr by default
    ]
)
logger = logging.getLogger(__name__)
# Quiet down pytaigaclient library logging if needed
logging.getLogger("pytaigaclient").setLevel(logging.WARNING)

# --- Taiga API 환경 변수 설정 및 클라이언트 초기화 ---
TAIGA_API_URL = os.environ.get("TAIGA_API_URL")
TAIGA_USERNAME = os.environ.get("TAIGA_USERNAME")
TAIGA_PASSWORD = os.environ.get("TAIGA_PASSWORD")
TAIGA_DEFAULT_PROJECT = os.environ.get("TAIGA_DEFAULT_PROJECT")

# 전역 변수로 Taiga 클라이언트 및 기본 프로젝트 설정
api = None
default_project = int(TAIGA_DEFAULT_PROJECT) if TAIGA_DEFAULT_PROJECT is not None else None

# 기본 프로젝트 설정 확인
if TAIGA_DEFAULT_PROJECT:
    logger.info(f"Default Taiga project set to: {TAIGA_DEFAULT_PROJECT}")
else:
    logger.warning("TAIGA_DEFAULT_PROJECT not set")

assert TAIGA_API_URL is not None
api = TaigaClient(host=TAIGA_API_URL)

# MCP 서버 설정
mcp = FastMCP(
    "Taiga MCP",
    dependencies=["pytaigaclient"]
)

def login():
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
    try:
        # 사용자 이름과 비밀번호가 제공된 경우 로그인 시도
        if TAIGA_USERNAME and TAIGA_PASSWORD:
            logger.info(f"Attempting to login with username: {TAIGA_USERNAME}")
            login_success = api.auth.login(
                username=TAIGA_USERNAME, 
                password=TAIGA_PASSWORD
            )
            if login_success:
                logger.info("Successfully logged in to Taiga API")
            else:
                logger.error("Failed to login to Taiga API")
    except TaigaException as e:
        logger.error(
            f"Taiga login failed for user '{TAIGA_USERNAME}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during login for user '{TAIGA_USERNAME}': {e}", exc_info=True)
        # Wrap unexpected errors in TaigaException if needed, or re-raise
        raise TaigaException(f"Unexpected login error: {e}")

login()

@mcp.tool("list_projects")
def list_projects(
    member: Optional[int] = None,
    members: Optional[str] = None,
    is_looking_for_people: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    is_backlog_activated: Optional[bool] = None,
    is_kanban_activated: Optional[bool] = None,
    order_by: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve projects from Taiga with various filtering options.
    
    Args:
        member: Member ID to filter projects
        members: Member IDs to filter projects (comma-separated)
        is_looking_for_people: Filter projects that are looking for new members
        is_featured: Filter projects highlighted by instance staff
        is_backlog_activated: Filter projects with active backlog
        is_kanban_activated: Filter projects with active kanban
        order_by: Field to order the results by (e.g., 'total_fans', 'total_activity')
    
    Returns:
        List of projects matching the criteria
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
    
    # Prepare filters
    params = {}
    
    # Add all provided filters to the params dictionary
    if member is not None:
        params["member"] = member
    if members is not None:
        # Convert comma-separated values to list
        params["members"] = members.split(",")
    if is_looking_for_people is not None:
        params["is_looking_for_people"] = is_looking_for_people
    if is_featured is not None:
        params["is_featured"] = is_featured
    if is_backlog_activated is not None:
        params["is_backlog_activated"] = is_backlog_activated
    if is_kanban_activated is not None:
        params["is_kanban_activated"] = is_kanban_activated
    if order_by is not None:
        params["order_by"] = order_by
    
    try:
        # Projects.list() expects key-value arguments, so we pass params as **kwargs
        projects = api.projects.list(**params)
        logger.info(f"Fetched {len(projects)} projects from Taiga")
        # Convert project objects to dictionaries if needed
        return [project.__dict__ if hasattr(project, "__dict__") else project for project in projects]
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to fetch projects: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching projects: {e}", exc_info=True)
        raise TaigaException(f"Error fetching projects: {e}")

@mcp.tool("get_project_info")
def get_project_info(project_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Retrieve comprehensive information about a Taiga project including status categories.
    
    Args:
        project_id: ID of the project to retrieve information for. If not specified, the default project will be used.
        
    Returns:
        Dictionary containing project details, user story statuses.
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
    
    # Use default project if not specified
    if project_id is None:
        project_id = default_project
        
    if project_id is None:
        raise TaigaException("No project ID specified and no default project configured")
    
    try:
        # Fetch project details
        project = api.projects.get(project_id)
        project_name = project if hasattr(project, 'name') else None
        logger.info(f"Retrieved information for project: {project_name}")
        
        # Fetch user story statuses
        user_story_statuses = api.userstory_statuses.list({"project": project_id})
        logger.info(f"Retrieved {len(user_story_statuses)} user story statuses")
        
        # Fetch task statuses
        # task_statuses = api.tasks.list(project=project_id)
        # logger.info(f"Retrieved {len(task_statuses)} task statuses")
        
        # Prepare the response
        result = {
            "project": project.__dict__ if hasattr(project, "__dict__") else project,
            "user_story_statuses": [status.__dict__ if hasattr(status, "__dict__") else status for status in user_story_statuses]
        }
        
        return result
    
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed while retrieving project info: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to retrieve project information: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while retrieving project information: {e}", exc_info=True)
        raise TaigaException(f"Error retrieving project information: {e}")

@mcp.tool("list_user_stories")
def list_user_stories(
    project: Optional[int] = None,
    milestone: Optional[int] = None,
    milestone__isnull: Optional[bool] = None,
    status: Optional[int] = None,
    status__is_archived: Optional[bool] = None,
    tags: Optional[str] = None,
    watchers: Optional[int] = None,
    assigned_to: Optional[int] = None,
    epic: Optional[int] = None,
    role: Optional[int] = None,
    status__is_closed: Optional[bool] = None,
    exclude_status: Optional[str] = None,
    exclude_tags: Optional[str] = None,
    exclude_assigned_to: Optional[int] = None,
    exclude_role: Optional[int] = None,
    exclude_epic: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve user stories from Taiga with various filtering options.
    
    Args:
        project: Project ID to filter user stories
        milestone: Milestone ID to filter user stories
        milestone__isnull: Filter user stories with or without milestone
        status: Status ID to filter user stories
        status__is_archived: Filter archived or non-archived user stories
        tags: Tags to filter user stories (comma-separated)
        watchers: Watcher user ID to filter user stories
        assigned_to: User ID stories are assigned to
        epic: Epic ID to filter user stories
        role: Role ID to filter user stories
        status__is_closed: Filter closed or open user stories
        exclude_status: Exclude stories with this status ID (comma-separated)
        exclude_tags: Exclude stories with these tags (comma-separated)
        exclude_assigned_to: Exclude stories assigned to this user
        exclude_role: Exclude stories with this role ID
        exclude_epic: Exclude stories from this epic ID
    
    Returns:
        List of user stories matching the criteria
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
    
    # Use default project if not specified
    if project is None:
        project = default_project
    
    # Prepare filters
    params = {}
    
    # Add all provided filters
    if project is not None:
        params["project"] = project
    if milestone is not None:
        params["milestone"] = milestone
    if milestone__isnull is not None:
        params["milestone__isnull"] = milestone__isnull
    if status is not None:
        params["status"] = status
    if status__is_archived is not None:
        params["status__is_archived"] = status__is_archived
    if tags is not None:
        params["tags"] = tags.split(",")
    if watchers is not None:
        params["watchers"] = watchers
    if assigned_to is not None:
        params["assigned_to"] = assigned_to
    if epic is not None:
        params["epic"] = epic
    if role is not None:
        params["role"] = role
    if status__is_closed is not None:
        params["status__is_closed"] = status__is_closed
    if exclude_status is not None:
        params["exclude_status"] = exclude_status
    if exclude_tags is not None:
        params["exclude_tags"] = exclude_tags.split(",")
    if exclude_assigned_to is not None:
        params["exclude_assigned_to"] = exclude_assigned_to
    if exclude_role is not None:
        params["exclude_role"] = exclude_role
    if exclude_epic is not None:
        params["exclude_epic"] = exclude_epic
    
    try:
        # Use the TaigaClient to fetch user stories with the filters
        user_stories = api.user_stories.list(**params)
        logger.info(f"Fetched {len(user_stories)} user stories from Taiga")
        # Convert user story objects to dictionaries if needed
        return [story.__dict__ if hasattr(story, "__dict__") else story for story in user_stories]
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to fetch user stories: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching user stories: {e}", exc_info=True)
        raise TaigaException(f"Error fetching user stories: {e}")


@mcp.tool("get_user_story")
def get_user_story(user_story_id: int) -> Dict[str, Any]:
    """
    Retrieve detailed information for a user story by its ID.
    
    Args:
        user_story_id: ID of the user story to retrieve
    
    Returns:
        Dictionary containing user story details and comments
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
        
    try:
        # Get user story by ID
        user_story = api.user_stories.get(user_story_id)
        if user_story is None:
            raise TaigaException(f"User story with ID {user_story_id} not found")

        # Check if user story has comments, and fetch them if it does
        total_comments = user_story.get("total_comments", 0)
        logger.debug(f"User story {user_story_id} has {total_comments} comments")

        comments = []
        if total_comments > 0:
            comments = api.user_stories.list_comments(user_story_id)
            logger.debug(f"Retrieved {len(comments)} comments for user story {user_story_id}")

        logger.info(f"Retrieved user story: ID {user_story_id}")
        
        # Create result dictionary with both story data and comments
        result = {
            "user_story": user_story,
            "comments": comments
        }

        return result
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to fetch user story: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching user story: {e}", exc_info=True)
        raise TaigaException(f"Error fetching user story: {e}")

@mcp.tool("get_user_story_by_ref")
def get_user_story_by_ref(ref: int, project: Optional[int] = None) -> Dict[str, Any]:
    """
    Retrieve detailed information for a user story by its reference number and project.
    
    Args:
        ref: Reference number of the user story within the project
        project: Project ID
    
    Returns:
        Dictionary containing user story details
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
        
    if project is None:
        if default_project is None:
            raise TaigaException("No project ID specified and no default project configured")
        project = default_project

    try:
        # Get user story by reference number and project ID
        user_story = api.user_stories.get_by_ref(ref=ref, project=project)
        if user_story is None:
            raise TaigaException(f"User story with reference #{ref} not found in project {project}")

        logger.info(f"Retrieved user story: Reference #{ref} in project {project}")
        
        return user_story
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to fetch user story by reference: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching user story by reference: {e}", exc_info=True)
        raise TaigaException(f"Error fetching user story by reference: {e}")


@mcp.tool("list_tasks")
def list_tasks(
    project: Optional[int] = None,
    milestone: Optional[int] = None,
    status: Optional[int] = None,
    assigned_to: Optional[int] = None,
    user_story: Optional[int] = None,
    tags: Optional[str] = None,
    role: Optional[int] = None,
    owner: Optional[int] = None,
    watchers: Optional[int] = None,
    status__is_closed: Optional[bool] = None,
    exclude_status: Optional[str] = None,
    exclude_tags: Optional[str] = None,
    exclude_role: Optional[int] = None,
    exclude_owner: Optional[int] = None,
    exclude_assigned_to: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve tasks from a Taiga project with various filtering options.
    
    Args:
        project: Project ID
        status: Status ID
        tags: Tags to filter tasks (comma-separated)
        user_story: User story ID
        role: Role ID
        owner: Owner user ID
        milestone: Milestone ID
        watchers: Watcher user ID
        assigned_to: User ID tasks are assigned to
        status__is_closed: Filter closed or open tasks (true|false)
        exclude_status: Exclude tasks with this status ID (comma-separated)
        exclude_tags: Exclude tasks with these tags (comma-separated)
        exclude_role: Exclude tasks with this role ID
        exclude_owner: Exclude tasks owned by this user ID
        exclude_assigned_to: Exclude tasks assigned to this user ID
    
    Returns:
        List of tasks matching the criteria
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
    
    # Use default project if not specified
    if project is None:
        project = default_project
    
    # Prepare filters
    params = {}
    
    # Add all provided filters to the params dictionary
    if project is not None:
        params["project"] = project
    if milestone is not None:
        params["milestone"] = milestone
    if status is not None:
        params["status"] = status
    if assigned_to is not None:
        params["assigned_to"] = assigned_to
    if user_story is not None:
        params["user_story"] = user_story
    if tags is not None:
        params["tags"] = tags.split(",")
    if role is not None:
        params["role"] = role
    if owner is not None:
        params["owner"] = owner
    if status__is_closed is not None:
        params["status__is_closed"] = status__is_closed
    if watchers is not None:
        params["watchers"] = watchers
    if exclude_status is not None:
        params["exclude_status"] = exclude_status
    if exclude_tags is not None:
        params["exclude_tags"] = exclude_tags.split(",")
    if exclude_role is not None:
        params["exclude_role"] = exclude_role
    if exclude_owner is not None:
        params["exclude_owner"] = exclude_owner
    if exclude_assigned_to is not None:
        params["exclude_assigned_to"] = exclude_assigned_to
    
    try:
        # Tasks.list() accepts a single query_params dictionary
        tasks = api.tasks.list(query_params=params)
        logger.info(f"Fetched {len(tasks)} tasks from Taiga")
        # Convert task objects to dictionaries if needed
        return [task.__dict__ if hasattr(task, "__dict__") else task for task in tasks]
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to fetch tasks: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching tasks: {e}", exc_info=True)
        raise TaigaException(f"Error fetching tasks: {e}")

@mcp.tool("get_task")
def get_task(task_id: int) -> Dict[str, Any]:
    """
    Retrieve detailed information for a task by its ID.
    
    Args:
        task_id: ID of the task to retrieve
        
    Returns:
        Dictionary containing task details
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
    
    try:
        # Get task by ID
        task = api.tasks.get(task_id)
        logger.info(f"Retrieved task: {task_id}")
        # Convert task object to dictionary
        return task.__dict__ if hasattr(task, "__dict__") else task
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to fetch task {task_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching task {task_id}: {e}", exc_info=True)
        raise TaigaException(f"Error fetching task: {e}")

@mcp.tool("get_task_by_ref")
def get_task_by_ref(ref: int, project: Optional[int] = None) -> Dict[str, Any]:
    """
    Retrieve detailed information for a task by its reference number and project.
    
    Args:
        ref: Reference number of the task within the project
        project: Project ID
    
    Returns:
        Dictionary containing task details
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
        
    if project is None:
        if default_project is None:
            raise TaigaException("No project ID specified and no default project configured")
        project = default_project

    try:
        # Get task by reference number and project ID
        task = api.tasks.get_by_ref(ref=ref, project=project)
        if task is None:
            raise TaigaException(f"Task with reference #{ref} not found in project {project}")

        logger.info(f"Retrieved task: Reference #{ref} in project {project}")
        
        return task.__dict__ if hasattr(task, "__dict__") else task
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to fetch task by reference: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching task by reference: {e}", exc_info=True)
        raise TaigaException(f"Error fetching task by reference: {e}")

@mcp.tool("list_issues")
def list_issues(
    project: Optional[int] = None,
    status: Optional[int] = None,
    severity: Optional[int] = None,
    priority: Optional[int] = None,
    owner: Optional[int] = None,
    assigned_to: Optional[int] = None,
    tags: Optional[str] = None,
    type: Optional[int] = None,
    role: Optional[int] = None, 
    watchers: Optional[int] = None,
    status__is_closed: Optional[bool] = None,
    exclude_status: Optional[str] = None,
    exclude_severity: Optional[int] = None,
    exclude_priority: Optional[int] = None,
    exclude_owner: Optional[int] = None,
    exclude_assigned_to: Optional[int] = None,
    exclude_tags: Optional[str] = None,
    exclude_type: Optional[int] = None,
    exclude_role: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve issues from a Taiga project with various filtering options.
    
    Args:
        project: Project ID
        status: Status ID
        severity: Severity ID
        priority: Priority ID
        owner: Owner user ID
        assigned_to: User ID issues are assigned to
        tags: Tags to filter issues (comma-separated)
        type: Issue type ID
        role: Role ID
        watchers: Watcher user ID
        status__is_closed: Filter closed or open issues (true|false)
        exclude_status: Exclude issues with this status ID (comma-separated)
        exclude_severity: Exclude issues with this severity ID
        exclude_priority: Exclude issues with this priority ID
        exclude_owner: Exclude issues owned by this user ID
        exclude_assigned_to: Exclude issues assigned to this user ID
        exclude_tags: Exclude issues with these tags (comma-separated)
        exclude_type: Exclude issues with this type ID
        exclude_role: Exclude issues with this role ID
    
    Returns:
        List of issues matching the criteria
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
    
    # Use default project if not specified
    if project is None:
        project = default_project
    
    # Prepare filters
    params = {}
    
    # Add all provided filters to the params dictionary
    if project is not None:
        params["project"] = project
    if status is not None:
        params["status"] = status
    if severity is not None:
        params["severity"] = severity
    if priority is not None:
        params["priority"] = priority
    if owner is not None:
        params["owner"] = owner
    if assigned_to is not None:
        params["assigned_to"] = assigned_to
    if tags is not None:
        params["tags"] = tags.split(",")
    if type is not None:
        params["type"] = type
    if role is not None:
        params["role"] = role
    if watchers is not None:
        params["watchers"] = watchers
    if status__is_closed is not None:
        params["status__is_closed"] = status__is_closed
    if exclude_status is not None:
        params["exclude_status"] = exclude_status
    if exclude_severity is not None:
        params["exclude_severity"] = exclude_severity
    if exclude_priority is not None:
        params["exclude_priority"] = exclude_priority
    if exclude_owner is not None:
        params["exclude_owner"] = exclude_owner
    if exclude_assigned_to is not None:
        params["exclude_assigned_to"] = exclude_assigned_to
    if exclude_tags is not None:
        params["exclude_tags"] = exclude_tags.split(",")
    if exclude_type is not None:
        params["exclude_type"] = exclude_type
    if exclude_role is not None:
        params["exclude_role"] = exclude_role
    
    try:
        # Issues.list() accepts a single query_params dictionary
        issues = api.issues.list(query_params=params)
        logger.info(f"Fetched {len(issues)} issues from Taiga")
        # Convert issue objects to dictionaries if needed
        return [issue.__dict__ if hasattr(issue, "__dict__") else issue for issue in issues]
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to fetch issues: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching issues: {e}", exc_info=True)
        raise TaigaException(f"Error fetching issues: {e}")

@mcp.tool("get_issue")
def get_issue(issue_id: int) -> Dict[str, Any]:
    """
    Retrieve detailed information for an issue by its ID.
    
    Args:
        issue_id: ID of the issue to retrieve
        
    Returns:
        Dictionary containing issue details
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
    
    try:
        # Get issue by ID
        issue = api.issues.get(issue_id)
        logger.info(f"Retrieved issue: {issue_id}")
        # Convert issue object to dictionary
        return issue.__dict__ if hasattr(issue, "__dict__") else issue
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to fetch issue {issue_id}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching issue {issue_id}: {e}", exc_info=True)
        raise TaigaException(f"Error fetching issue: {e}")

@mcp.tool("get_issue_by_ref")
def get_issue_by_ref(ref: int, project: Optional[int] = None) -> Dict[str, Any]:
    """
    Retrieve detailed information for an issue by its reference number and project.
    
    Args:
        ref: Reference number of the issue within the project
        project: Project ID
    
    Returns:
        Dictionary containing issue details
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
        
    if project is None:
        if default_project is None:
            raise TaigaException("No project ID specified and no default project configured")
        project = default_project

    try:
        # Get issue by reference number and project ID
        issue = api.issues.get_by_ref(ref=ref, project=project)
        if issue is None:
            raise TaigaException(f"Issue with reference #{ref} not found in project {project}")

        logger.info(f"Retrieved issue: Reference #{ref} in project {project}")
        
        return issue.__dict__ if hasattr(issue, "__dict__") else issue
    except TaigaAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise TaigaException(f"Authentication error: {e}")
    except TaigaException as e:
        logger.error(f"Failed to fetch issue by reference: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching issue by reference: {e}", exc_info=True)
        raise TaigaException(f"Error fetching issue by reference: {e}")

# --- Run the server ---
if __name__ == "__main__":
    mcp.run()