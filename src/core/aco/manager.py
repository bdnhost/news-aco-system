# src/core/aco/manager.py
from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import logging


@dataclass
class NewsSource:
    """מייצג מקור חדשות בודד"""

    url: str
    name: str
    category: str
    last_visit: Optional[datetime] = None
    pheromone_level: float = 1.0
    quality_score: float = 0.0
    visit_count: int = 0


@dataclass
class SourceQuality:
    """מייצג מדדי איכות של מקור"""

    relevance: float = 0.0
    freshness: float = 0.0
    reliability: float = 0.0
    coverage: float = 0.0

    def total_score(self) -> float:
        """מחשב ציון איכות כולל"""
        weights = {
            "relevance": 0.4,
            "freshness": 0.3,
            "reliability": 0.2,
            "coverage": 0.1,
        }
        return sum(getattr(self, attr) * weight for attr, weight in weights.items())


class ACOManager:
    """מנהל אלגוריתם ACO עבור איסוף חדשות"""

    def __init__(
        self,
        evaporation_rate: float = 0.1,
        exploration_rate: float = 0.2,
        min_pheromone: float = 0.1,
        max_pheromone: float = 5.0,
    ):
        self.sources: Dict[str, NewsSource] = {}
        self.evaporation_rate = evaporation_rate
        self.exploration_rate = exploration_rate
        self.min_pheromone = min_pheromone
        self.max_pheromone = max_pheromone
        self.logger = logging.getLogger(__name__)

    async def add_source(self, url: str, name: str, category: str) -> NewsSource:
        """הוספת מקור חדשות חדש"""
        if url in self.sources:
            self.logger.warning(f"Source {url} already exists")
            return self.sources[url]

        source = NewsSource(url=url, name=name, category=category)
        self.sources[url] = source
        return source

    async def select_next_source(self, category: Optional[str] = None) -> NewsSource:
        """בחירת המקור הבא לסריקה על פי אלגוריתם ACO"""
        available_sources = [
            s
            for s in self.sources.values()
            if (not category or s.category == category) and self._is_source_available(s)
        ]

        if not available_sources:
            raise ValueError("No available sources")

        # בחירה אקראית לצורך אקספלורציה
        if np.random.random() < self.exploration_rate:
            return np.random.choice(available_sources)

        # בחירה מבוססת פרומונים
        total_pheromone = sum(s.pheromone_level for s in available_sources)
        probabilities = [s.pheromone_level / total_pheromone for s in available_sources]

        return np.random.choice(available_sources, p=probabilities)

    async def update_source_quality(
        self, source_url: str, quality: SourceQuality
    ) -> None:
        """עדכון איכות המקור והפרומונים"""
        if source_url not in self.sources:
            raise ValueError(f"Unknown source: {source_url}")

        source = self.sources[source_url]
        quality_score = quality.total_score()

        # עדכון פרומונים
        new_pheromone = (
            1 - self.evaporation_rate
        ) * source.pheromone_level + self.evaporation_rate * quality_score

        # הגבלת ערכי הפרומונים
        source.pheromone_level = np.clip(
            new_pheromone, self.min_pheromone, self.max_pheromone
        )

        # עדכון נתוני המקור
        source.quality_score = quality_score
        source.last_visit = datetime.now()
        source.visit_count += 1

        self.logger.info(
            f"Updated source {source.name}: "
            f"quality={quality_score:.2f}, "
            f"pheromone={source.pheromone_level:.2f}"
        )

    async def evaporate_pheromones(self) -> None:
        """דעיכת פרומונים גלובלית"""
        for source in self.sources.values():
            source.pheromone_level *= 1 - self.evaporation_rate
            if source.pheromone_level < self.min_pheromone:
                source.pheromone_level = self.min_pheromone

    def _is_source_available(self, source: NewsSource) -> bool:
        """בדיקה האם מקור זמין לסריקה"""
        if not source.last_visit:
            return True

        # חישוב מרווח הזמן המינימלי בין ביקורים
        min_interval = timedelta(minutes=30)  # ברירת מחדל
        if source.quality_score > 0.8:
            min_interval = timedelta(minutes=15)
        elif source.quality_score < 0.3:
            min_interval = timedelta(hours=1)

        return datetime.now() - source.last_visit > min_interval

    async def get_source_stats(self) -> Dict:
        """קבלת סטטיסטיקות על המקורות"""
        return {
            "total_sources": len(self.sources),
            "active_sources": sum(1 for s in self.sources.values() if s.last_visit),
            "avg_quality": np.mean([s.quality_score for s in self.sources.values()]),
            "avg_pheromone": np.mean(
                [s.pheromone_level for s in self.sources.values()]
            ),
        }
