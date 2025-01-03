from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio

class BaseAgent(ABC):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.active = False
        self.stats = {'processed': 0, 'errors': 0}
        
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data according to agent's role"""
        pass
    
    async def start(self):
        """Start agent's processing loop"""
        self.active = True
        while self.active:
            try:
                await self._process_cycle()
            except Exception as e:
                self.stats['errors'] += 1
                # Log error
            await asyncio.sleep(1)
            
    async def stop(self):
        """Stop agent's processing"""
        self.active = False
