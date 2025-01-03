import spacy
from typing import Dict, List, Optional
from datetime import datetime

class ContentProcessor:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_lg')
        
    async def process_content(self, 
                            content: str, 
                            metadata: Dict = None) -> Dict:
        """Process news content using NLP"""
        doc = self.nlp(content)
        
        # Extract key information
        entities = self._extract_entities(doc)
        keywords = self._extract_keywords(doc)
        summary = self._generate_summary(doc)
        sentiment = self._analyze_sentiment(doc)
        
        return {
            'entities': entities,
            'keywords': keywords,
            'summary': summary,
            'sentiment': sentiment,
            'processed_at': datetime.now().isoformat()
        }
        
    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        return entities
    
    def _extract_keywords(self, doc, top_k: int = 10) -> List[str]:
        """Extract key terms from text"""
        keywords = []
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                token.pos_ in ['NOUN', 'PROPN']):
                keywords.append(token.text)
        return list(set(keywords))[:top_k]
    
    def _generate_summary(self, doc, max_sentences: int = 3) -> str:
        """Generate brief summary of content"""
        sentences = list(doc.sents)
        if len(sentences) <= max_sentences:
            return doc.text
            
        # Simple extractive summarization
        sentence_scores = []
        for sent in sentences:
            score = sum(1 for token in sent 
                       if not token.is_stop and not token.is_punct)
            sentence_scores.append((sent, score))
            
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        summary_sents = [sent.text for sent, _ in sentence_scores[:max_sentences]]
        return ' '.join(summary_sents)
    
    def _analyze_sentiment(self, doc) -> float:
        """Basic sentiment analysis"""
        return sum(token.sentiment for token in doc) / len(doc)
