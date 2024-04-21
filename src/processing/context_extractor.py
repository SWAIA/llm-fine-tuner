from typing import Dict, List
from transformers import AutoTokenizer, pipeline, set_seed
from src.utils import LoggerService

class ContextExtractor:

    def __init__(self, config: Dict[str, str]):
        self.config = config
        self._initialize_pipelines()

    async def _initialize_pipelines(self):
        try:
            set_seed(42)
            self.sentiment_pipeline = pipeline('sentiment-analysis', model=AutoTokenizer.from_pretrained('distilbert-base-uncased'))
            self.ner_pipeline = pipeline('ner', model=AutoTokenizer.from_pretrained('dbmdz/bert-large-cased-finetuned-conll03-english'))

        except Exception as e:
            await LoggerService.get_instance().log("error", f"Failed to initialize NLP pipelines: {e}")

    async def extract_enhanced_context(self, file_text: str) -> Dict[str, str]:
        try:
            paragraphs = self._split_into_paragraphs(file_text)
            return {
                'surrounding_text': self._extract_surrounding_text(paragraphs),
                'section_headers': self._extract_section_headers(paragraphs),
                'named_entities': await self._extract_named_entities(file_text),
                'sentiment_score': await self._analyze_sentiment(file_text),
                'code_examples': self.check_for_code_examples(file_text),
                'content_type': self.determine_content_type(file_text),
            }
        except Exception as e:
            await LoggerService.get_instance().log("error", f"Error extracting enhanced context: {e}")
            return {}

    def _split_into_paragraphs(self, text: str) -> List[str]:
        return text.split('\n\n')

    def _extract_surrounding_text(self, paragraphs: List[str]) -> List[str]:
        num_surrounding_paragraphs = self.config.get('context_options', {}).get('num_surrounding_paragraphs', 3)
        return paragraphs[:num_surrounding_paragraphs] + paragraphs[-num_surrounding_paragraphs:]

    def _extract_section_headers(self, paragraphs: List[str]) -> List[str]:
        return [p.split('\n', 1)[0] for p in paragraphs if p.startswith('# ')]

    async def _extract_named_entities(self, text: str) -> List[str]:
        try:
            # Assuming the ner_pipeline method accepts text and returns entities
            return [entity['word'] for entity in self.ner_pipeline(text)]
        except Exception as e:
            await LoggerService.get_instance().log("error", f"Error extracting named entities: {e}")
            return []

    async def _analyze_sentiment(self, text: str) -> float:
        try:
            result = self.sentiment_pipeline(text)
            return result[0]['score']
        except Exception as e:
            await LoggerService.get_instance().log("error", f"Error analyzing sentiment: {e}")
            return 0.0   
         
    def check_for_code_examples(self, text: str) -> bool:
        # Example logic to detect code snippets
        code_markers = ['def ', 'class ', '#include', '<div', '{', '}', 'function ']
        return any(marker in text for marker in code_markers)

    def determine_content_type(self, text: str) -> str:
        if self.check_for_code_examples(text):
            return 'Technical'
        if any(word in text.lower() for word in ['tutorial', 'guide', 'how-to']):
            return 'Instructional'
        return 'General'

    async def analyze_sentiment(self, text: str) -> str:
        # Removed redundant pipeline initialization as it's already done in _initialize_pipelines
        result = self.sentiment_pipeline(text)[0]
        if result['label'] == 'NEGATIVE':
            return 'negative'
        elif result['label'] == 'POSITIVE':
            return 'positive'
        else:
            return 'neutral'