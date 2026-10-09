from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Iterator

from application.pages.export_items.models import (
    Item,
    FeatureQuestion,
)


class IItemRepository(ABC):
    """Interface for item data access."""

    @abstractmethod
    def get_items(
        self,
        filters: dict,
        fields: list[str],
        feature_profile: str,
    ) -> Iterator[Item]:
        """Fetch items from the data source.

        Args:
            filters: Dict with optional keys 'state', 'item_line', 'search'
            fields: List of field names to include in the export
            feature_profile: Profile code for feature questions (e.g., 'PRODUCTO')

        Returns:
            Iterator of Item objects with requested fields populated
        """
        ...

    @abstractmethod
    def get_lines(self) -> dict[str, str]:
        """Get item lines for filter dropdown.

        Returns:
            Dict mapping line name to line code
        """
        ...

    @abstractmethod
    def get_feature_questions(self, feature_profile: str) -> OrderedDict[int, FeatureQuestion]:
        """Get feature questions for a profile (used to build column headers).

        Args:
            feature_profile: Profile code (e.g., 'PRODUCTO')

        Returns:
            OrderedDict mapping line_no to FeatureQuestion
        """
        ...
