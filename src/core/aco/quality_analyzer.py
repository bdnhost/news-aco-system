# src/core/aco/quality_analyzer.py
from typing import List, Dict
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass


@dataclass
class Article:
    """מייצג מאמר חדשותי בודד"""

    title: str
    content: str
    publish_date: datetime
    entities: List[str]
    keywords: List[str]
    word_count: int


class QualityAnalyzer:
    """מנתח איכות של מקורות חדשות"""

    def __init__(self):
        self.topic_weights = {}  # משקלות לנושאים שונים
        self.recent_articles: Dict[str, List[Article]] = {}  # מאמרים אחרונים לכל מקור

    def calculate_source_quality(
        self, source_url: str, new_articles: List[Article]
    ) -> SourceQuality:
        """חישוב מדדי איכות למקור"""

        # עדכון מאגר המאמרים
        if source_url not in self.recent_articles:
            self.recent_articles[source_url] = []
        self.recent_articles[source_url].extend(new_articles)

        # שמירת רק המאמרים מהשבוע האחרון
        week_ago = datetime.now() - timedelta(days=7)
        self.recent_articles[source_url] = [
            article
            for article in self.recent_articles[source_url]
            if article.publish_date > week_ago
        ]

        # חישוב מדדי איכות
        relevance = self._calculate_relevance(new_articles)
        freshness = self._calculate_freshness(new_articles)
        reliability = self._calculate_reliability(source_url)
        coverage = self._calculate_coverage(source_url)

        return SourceQuality(
            relevance=relevance,
            freshness=freshness,
            reliability=reliability,
            coverage=coverage,
        )

    def _calculate_relevance(self, articles: List[Article]) -> float:
        """חישוב רלוונטיות המאמרים"""
        if not articles:
            return 0.0

        relevance_scores = []
        for article in articles:
            # חישוב התאמה לנושאים חשובים
            topic_score = sum(
                self.topic_weights.get(keyword, 0) for keyword in article.keywords
            )

            # בדיקת אורך המאמר
            length_score = min(article.word_count / 500, 1.0)

            # בדיקת מספר הישויות
            entity_score = min(len(article.entities) / 10, 1.0)

            relevance_scores.append(
                0.5 * topic_score + 0.3 * length_score + 0.2 * entity_score
            )

        return np.mean(relevance_scores)

    def _calculate_freshness(self, articles: List[Article]) -> float:
        """חישוב טריות המאמרים"""
        if not articles:
            return 0.0

        now = datetime.now()
        age_scores = []

        for article in articles:
            age = now - article.publish_date

            # מאמרים מהשעה האחרונה מקבלים ציון מלא
            if age < timedelta(hours=1):
                score = 1.0
            # דעיכה לוגריתמית של הציון
            else:
                hours_old = age.total_seconds() / 3600
                score = max(0, 1 - np.log2(hours_old) / 10)

            age_scores.append(score)

        return np.mean(age_scores)

    def _calculate_reliability(self, source_url: str) -> float:
        """חישוב אמינות המקור"""
        if source_url not in self.recent_articles:
            return 0.0

        articles = self.recent_articles[source_url]
        if not articles:
            return 0.0

        # מדדים לאמינות
        avg_length = np.mean([a.word_count for a in articles])
        avg_entities = np.mean([len(a.entities) for a in articles])

        # ציון מבוסס על אורך ממוצע ומספר ישויות
        length_score = min(avg_length / 800, 1.0)
        entity_score = min(avg_entities / 15, 1.0)

        return 0.6 * length_score + 0.4 * entity_score

    def _calculate_coverage(self, source_url: str) -> float:
        """חישוב היקף הכיסוי של המקור"""
        if source_url not in self.recent_articles:
            return 0.0

        articles = self.recent_articles[source_url]
        if not articles:
            return 0.0

        # אוסף כל המילות מפתח והישויות
        all_keywords = set()
        all_entities = set()

        for article in articles:
            all_keywords.update(article.keywords)
            all_entities.update(article.entities)

        # ציון מבוסס על מגוון הנושאים והישויות
        keyword_score = min(len(all_keywords) / 100, 1.0)
        entity_score = min(len(all_entities) / 50, 1.0)

        return 0.7 * keyword_score + 0.3 * entity_score

    def update_topic_weights(self, weights: Dict[str, float]):
        """עדכון משקלות הנושאים"""
        self.topic_weights.update(weights)
