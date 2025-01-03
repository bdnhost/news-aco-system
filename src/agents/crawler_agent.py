from typing import Dict, Any, List
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from .base_agent import BaseAgent

class CrawlerAgent(BaseAgent):
    def __init__(self, agent_id: str, source_configs: List[Dict]):
        super().__init__(agent_id)
        self.source_configs = source_configs
        self.session = None
        
    async def setup(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            
    async def process(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Crawl news from a specific source"""
        if not self.session:
            await self.setup()
            
        try:
            async with self.session.get(source['url']) as response:
                if response.status == 200:
                    content = await response.text()
                    parsed_data = await self._parse_content(
                        content, 
                        source['selectors']
                    )
                    self.stats['processed'] += 1
                    return parsed_data
                else:
                    self.stats['errors'] += 1
                    return None
        except Exception as e:
            self.stats['errors'] += 1
            # Log error
            return None
            
    async def _parse_content(self, 
                            content: str, 
                            selectors: Dict) -> Dict[str, Any]:
        """Parse HTML content using BeautifulSoup"""
        soup = BeautifulSoup(content, 'html.parser')
        
        articles = []
        for article in soup.select(selectors['article']):
            articles.append({
                'title': self._extract_text(article, selectors['title']),
                'content': self._extract_text(article, selectors['content']),
                'url': self._extract_url(article, selectors['link']),
                'published': self._extract_date(article, selectors['date']),
                'crawled_at': datetime.now().isoformat()
            })
            
        return {
            'source_url': self.current_url,
            'articles': articles
        }
        
    def _extract_text(self, element, selector: str) -> str:
        """Extract text using CSS selector"""
        found = element.select_one(selector)
        return found.text.strip() if found else ''
        
    def _extract_url(self, element, selector: str) -> str:
        """Extract URL using CSS selector"""
        found = element.select_one(selector)
        return found.get('href', '') if found else ''
        
    def _extract_date(self, element, selector: str) -> str:
        """Extract and parse date using CSS selector"""
        found = element.select_one(selector)
        if not found:
            return datetime.now().isoformat()
            
        date_str = found.text.strip()
        try:
            # Add date parsing logic here
            return datetime.now().isoformat()
        except:
            return datetime.now().isoformat()
