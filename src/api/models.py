from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class Source(BaseModel):
    url: str
    name: str
    category: Optional[str]
    selectors: Dict[str, str]
    update_interval: int = 300  # seconds

class Article(BaseModel):
    title: str
    content: str
    url: str
    source: str
    published_date: datetime
    processed_date: datetime
    metadata: Optional[Dict] = None

class SystemStats(BaseModel):
    total_sources: int
    total_articles: int
    active_agents: int
    processing_rate: float
    last_update: datetime
