from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import TaigaClient


class Resource:
    """
    Base class for all Taiga API resources.
    """

    def __init__(self, client: "TaigaClient"):
        """
        Initialize a resource with a Taiga client.

        Args:
            client: The Taiga client instance.
        """
        self.client = client 