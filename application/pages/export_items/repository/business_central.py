"""Business Central repository - stub for future REST API implementation.

This module will contain the implementation for fetching items from
Microsoft Dynamics 365 Business Central via REST API when the database
migration is complete.
"""

from collections import OrderedDict
from typing import Iterator

from application.pages.export_items.models import Item, FeatureQuestion
from .interfaces import IItemRepository


class BusinessCentralRepository(IItemRepository):
    """Repository implementation for Business Central REST API."""

    def __init__(self, api_url: str, api_key: str, company_id: str):
        self.api_url = api_url
        self.api_key = api_key
        self.company_id = company_id

    def get_items(
        self,
        filters: dict,
        fields: list[str],
        feature_profile: str,
    ) -> Iterator[Item]:
        """Fetch items from Business Central via REST API.

        TODO: Implement REST API calls to:
            GET {api_url}/companies({company_id})/items
            Filter by ?$filter=state eq 'ACTIVO'
            Select specific fields

        For features, need to call:
            GET {api_url}/companies({company_id})/itemCategories
            or custom extension endpoint for feature questionnaire
        """
        raise NotImplementedError("Business Central repository not yet implemented")

    def get_lines(self) -> dict[str, str]:
        """Get item lines from Business Central.

        TODO: GET {api_url}/companies({company_id})/itemLines
        """
        raise NotImplementedError("Business Central repository not yet implemented")

    def get_feature_questions(self, feature_profile: str) -> OrderedDict[int, FeatureQuestion]:
        """Get feature questions from Business Central.

        TODO: Custom extension endpoint or item attribute table
        """
        raise NotImplementedError("Business Central repository not yet implemented")
