from typing import Dict, Any, List
import logging
from utils import extract_text_from_file, get_models_and_pipelines

class ContextExtractor:
    def __init__(self, config: Dict[str, Any]):
        if not isinstance(config, dict):
            raise TypeError("Config must be a dictionary.")
        self.config = config
        self._initialize_pipelines()

    # Initialize NLP pipelines for context extraction
    def _initialize_pipelines(self) -> None:
        models_and_pipelines = get_models_and_pipelines()
        if models_and_pipelines is None:
            raise ValueError("Failed to load models and pipelines.")
        self.ner_pipeline = models_and_pipelines['ner_pipeline']
        self.sentiment_pipeline = models_and_pipelines['sentiment_pipeline']
        self.coref_pipeline = models_and_pipelines['coref_pipeline']
        self.event_pipeline = models_and_pipelines['event_pipeline']

    # Extracts context from the given file, enhancing it with NLP insights
    def extract_enhanced_context(self, file_path: str) -> Dict[str, Any]:
        if not isinstance(file_path, str):
            raise TypeError("file_path must be a string.")
        file_text = extract_text_from_file(file_path)
        if file_text is None:
            logging.error(f"Failed to extract text from file: {file_path}")
            return {}
        paragraphs = file_text.split('\n\n')
        
        # Configure the number of surrounding paragraphs to include
        num_surrounding_paragraphs = self.config.get('context_options', {}).get('num_surrounding_paragraphs', 3)
        if not isinstance(num_surrounding_paragraphs, int):
            logging.error("num_surrounding_paragraphs must be an integer.")
            num_surrounding_paragraphs = 3  # Default to 3 if not properly configured
        surrounding_text = paragraphs[:num_surrounding_paragraphs] + paragraphs[-num_surrounding_paragraphs:]
        section_headers = [paragraph.split('\n', 1)[0] for paragraph in paragraphs if paragraph.startswith('# ')]

        # Compile context information
        context = {
            'surrounding_text': surrounding_text,
            'section_headers': section_headers,
            'named_entities': self.extract_named_entities(file_text),
            'sentiment_score': self.analyze_sentiment(file_text),
            'coreferent_mentions': self.resolve_coreferences(file_text),
            'extracted_events': self.extract_events(file_text)
        }

        self.customize_context_extraction(context)

        return context
    # Extract named entities from text using NER pipeline
    def extract_named_entities(self, text: str) -> List[str]:
        if not isinstance(text, str):
            logging.error("Text input must be a string.")
            return []
        return [entity['word'] for entity in self.ner_pipeline(text)]

    # Analyze sentiment of the text and return sentiment score
    def analyze_sentiment(self, text: str) -> float:
        if not isinstance(text, str):
            logging.error("Text input must be a string.")
            return 0.0
        sentiment_output = self.sentiment_pipeline(text)
        return sentiment_output[0]['score'] if sentiment_output else logging.error("Failed to analyze sentiment.") or 0.0

    # Resolve coreferences in the text and return a list of mentions
    def resolve_coreferences(self, text: str) -> List[str]:
        if not isinstance(text, str):
            logging.error("Text input must be a string.")
            return []
        coref_output = self.coref_pipeline(text)
        return [mention['text'] for mention in coref_output] if coref_output else logging.error("Failed to resolve coreferences.") or []

    # Extract events from the text using event extraction pipeline
    def extract_events(self, text: str) -> List[str]:
        if not isinstance(text, str):
            logging.error("Text input must be a string.")
            return []
        events = self.event_pipeline(text)
        return [event['word'] for event in events] if events else logging.error("Failed to extract events.") or []

    # Customize context extraction based on configuration options
    def customize_context_extraction(self, context: Dict[str, Any]) -> None:
        if not isinstance(context, dict):
            logging.error("Context must be a dictionary.")
            return
        # Apply configuration options for context customization
        context_options = self.config.get('context_options', {})
        if not context_options.get('include_coref', True):
            context['coreferent_mentions'] = []
        if not context_options.get('include_events', True):
            context['extracted_events'] = []

# Tests because it is more convienient to have them in the same file
import unittest
from unittest.mock import patch, MagicMock

class TestContextExtractor(unittest.TestCase):
    def setUp(self):
        self.config = {'context_options': {'include_coref': True, 'include_events': True}}
        self.context_extractor = ContextExtractor(self.config)
        self.text = "This is a test text for context extraction."

    @patch('data_enrichment_context.ContextExtractor.extract_named_entities')
    @patch('data_enrichment_context.ContextExtractor.analyze_sentiment')
    @patch('data_enrichment_context.ContextExtractor.resolve_coreferences')
    @patch('data_enrichment_context.ContextExtractor.extract_events')
    def test_extract_enhanced_context(self, mock_extract_events, mock_resolve_coreferences, mock_analyze_sentiment, mock_extract_named_entities):
        mock_extract_named_entities.return_value = ['entity1', 'entity2']
        mock_analyze_sentiment.return_value = 0.5
        mock_resolve_coreferences.return_value = ['mention1', 'mention2']
        mock_extract_events.return_value = ['event1', 'event2']

        context = self.context_extractor.extract_enhanced_context(self.text)
        self.assertIsInstance(context, dict)
        self.assertIn('named_entities', context)
        self.assertIn('sentiment_score', context)
        self.assertIn('coreferent_mentions', context)
        self.assertIn('extracted_events', context)

        self.assertEqual(context['named_entities'], ['entity1', 'entity2'])
        self.assertEqual(context['sentiment_score'], 0.5)
        self.assertEqual(context['coreferent_mentions'], ['mention1', 'mention2'])
        self.assertEqual(context['extracted_events'], ['event1', 'event2'])

        mock_extract_named_entities.assert_called_once_with(self.text)
        mock_analyze_sentiment.assert_called_once_with(self.text)
        mock_resolve_coreferences.assert_called_once_with(self.text)
        mock_extract_events.assert_called_once_with(self.text)

if __name__ == '__main__':
    unittest.main()
