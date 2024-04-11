from typing import Dict, List
from transformers import AutoTokenizer, pipeline, set_seed
from ..utils import Utils

class ContextExtractor:

    def __init__(self, config: Dict[str, str]):
        self.config = config
        self._initialize_pipelines()

    def _initialize_pipelines(self):
        try:
            set_seed(42)
            self.sentiment_pipeline = pipeline('sentiment-analysis', model=AutoTokenizer.from_pretrained('distilbert-base-uncased'))
        except Exception as e:
            Utils.log_error(f"Failed to initialize NLP pipelines: {e}")

    def extract_enhanced_context(self, file_text: str) -> Dict[str, str]:
        try:
            paragraphs = self._split_into_paragraphs(file_text)
            context = {
                'surrounding_text': self._extract_surrounding_text(paragraphs),
                'section_headers': self._extract_section_headers(paragraphs),
                'named_entities': self._extract_named_entities(file_text),
                'sentiment_score': self._analyze_sentiment(file_text),
            }

            return context
        except Exception as e:
            Utils.log_error(f"Error extracting enhanced context: {e}")
            return {}

    def _split_into_paragraphs(self, text: str) -> List[str]:
        return text.split('\n\n')

    def _extract_surrounding_text(self, paragraphs: List[str]) -> List[str]:
        num_surrounding_paragraphs = self.config.get('context_options', {}).get('num_surrounding_paragraphs', 3)
        return paragraphs[:num_surrounding_paragraphs] + paragraphs[-num_surrounding_paragraphs:]

    def _extract_section_headers(self, paragraphs: List[str]) -> List[str]:
        return [p.split('\n', 1)[0] for p in paragraphs if p.startswith('# ')]

    def _extract_named_entities(self, text: str) -> List[str]:
        try:
            return [entity['word'] for entity in self.ner_pipeline(text)]
        except Exception as e:
            Utils.log_error(f"Error extracting named entities: {e}")
            return []

    def _analyze_sentiment(self, text: str) -> float:
        try:
            result = self.sentiment_pipeline(text)
            return result[0]['score']
        except Exception as e:
            Utils.log_error(f"Error analyzing sentiment: {e}")
            return 0.0
