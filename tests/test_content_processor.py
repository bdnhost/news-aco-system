import pytest
from src.core.content_processor import ContentProcessor

@pytest.fixture
def processor():
    return ContentProcessor()

def test_entity_extraction(processor):
    text = 'Microsoft CEO Satya Nadella announced new AI features in Windows.'
    result = processor._extract_entities(processor.nlp(text))
    
    assert 'Microsoft' in str(result)
    assert 'Satya Nadella' in str(result)
    assert 'Windows' in str(result)

def test_keyword_extraction(processor):
    text = 'Artificial Intelligence and Machine Learning are transforming technology.'
    keywords = processor._extract_keywords(processor.nlp(text))
    
    assert 'Intelligence' in keywords
    assert 'Learning' in keywords
    assert 'technology' in keywords
