from typing import Dict, List, Optional
import asyncio
import numpy as np
from datetime import datetime

class ACOSystem:
    def __init__(self, 
                 num_agents: int = 10,
                 evaporation_rate: float = 0.1,
                 exploration_rate: float = 0.2):
        self.num_agents = num_agents
        self.evaporation_rate = evaporation_rate
        self.exploration_rate = exploration_rate
        self.pheromone_matrix = {}
        self.quality_scores = {}
        self.last_update = {}
        
    async def initialize_sources(self, sources: List[str]):
        """Initialize pheromone trails for news sources"""
        for source in sources:
            self.pheromone_matrix[source] = 1.0
            self.quality_scores[source] = 0.0
            self.last_update[source] = datetime.now()
    
    async def select_source(self, available_sources: List[str]) -> str:
        """Select next news source using ACO algorithm"""
        if np.random.random() < self.exploration_rate:
            return np.random.choice(available_sources)
        
        scores = [self.pheromone_matrix.get(source, 0.0) 
                 for source in available_sources]
        probabilities = np.array(scores) / sum(scores)
        
        return np.random.choice(available_sources, p=probabilities)
    
    async def update_pheromone(self, source: str, quality_score: float):
        """Update pheromone levels for a source"""
        current_level = self.pheromone_matrix.get(source, 0.0)
        self.pheromone_matrix[source] = (
            current_level * (1 - self.evaporation_rate) +
            quality_score * self.evaporation_rate
        )
        self.quality_scores[source] = quality_score
        self.last_update[source] = datetime.now()
    
    async def evaporate_pheromones(self):
        """Global pheromone evaporation"""
        for source in self.pheromone_matrix:
            self.pheromone_matrix[source] *= (1 - self.evaporation_rate)
