from __future__ import annotations

from abc import ABC, abstractmethod

from creator_insights.config import Settings
from creator_insights.models import Note


class Source(ABC):
    @abstractmethod
    def collect(self, settings: Settings, limit: int) -> list[Note]:
        """Collect notes from a permitted data source."""

