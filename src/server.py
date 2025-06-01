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
    exclude_status: Optional[int] = None,
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
        exclude_status: Exclude stories with this status ID
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
    특정 ID의 사용자 스토리에 대한 상세 정보를 가져옵니다.
    
    Args:
        user_story_id: 조회할 사용자 스토리의 ID
    
    Returns:
        사용자 스토리 상세 정보를 담은 딕셔너리
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
        
    try:
        # API를 사용하여 특정 ID의 사용자 스토리 조회
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
    exclude_status: Optional[int] = None,
    exclude_tags: Optional[str] = None,
    exclude_role: Optional[int] = None,
    exclude_owner: Optional[int] = None,
    exclude_assigned_to: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Taiga 프로젝트 내의 작업(Task) 목록을 조회합니다.
    
    Args:
        project: 프로젝트 ID
        status: 상태 ID
        tags: 쉼표(,)로 구분된 태그
        user_story: 사용자 스토리 ID
        role: 역할 ID
        owner: 소유자 ID
        milestone: 마일스톤 ID
        watchers: 감시자 사용자 ID
        assigned_to: 할당된 사용자 ID
        status__is_closed: (true|false)
        exclude_status: 제외할 상태 ID
        exclude_tags: 쉼표(,)로 구분된 제외할 태그
        exclude_role: 제외할 역할 ID
        exclude_owner: 제외할 소유자 ID
        exclude_assigned_to: 제외할 할당 사용자 ID
    
    Returns:
        조건에 맞는 작업 목록
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
        # Tasks.list()는 단일 query_params 딕셔너리를 받으므로 params 전체를 전달합니다
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
    ID로 지정한 단일 작업(Task)의 상세 정보를 조회합니다.
    
    Args:
        task_id: 조회할 작업의 ID
        
    Returns:
        작업 상세 정보가 담긴 딕셔너리
    """
    if api is None:
        raise TaigaException("Taiga API client is not initialized")
    
    try:
        # 작업 ID로 단일 작업 조회
        task = api.tasks.get(task_id)
        logger.info(f"Retrieved task: {task_id}")
        # 작업 객체를 딕셔너리로 변환
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

# --- Run the server ---
if __name__ == "__main__":
    mcp.run()