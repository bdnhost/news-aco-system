import pytest
import aiohttp
from src.agents.crawler_agent import CrawlerAgent

@pytest.fixture
def source_config():
    return {
        'url': 'https://example.com',
        'selectors': {
            'article': 'div.article',
            'title': 'h1',
            'content': 'div.content',
            'link': 'a',
            'date': 'time'
        }
    }

@pytest.mark.asyncio
async def test_crawler_setup():
    agent = CrawlerAgent('test_agent', [])
    await agent.setup()
    assert isinstance(agent.session, aiohttp.ClientSession)
    await agent.cleanup()

@pytest.mark.asyncio
async def test_content_parsing(source_config):
    agent = CrawlerAgent('test_agent', [source_config])
    
    # Mock HTML content
    html_content = '''
    <div class="article">
        <h1>Test Title</h1>
        <div class="content">Test Content</div>
        <a href="/test">Link</a>
        <time>2024-01-04</time>
    </div>
    '''
    
    result = await agent._parse_content(html_content, source_config['selectors'])
    assert 'articles' in result
    assert len(result['articles']) > 0
    assert 'Test Title' in str(result)
