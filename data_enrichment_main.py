import json
import logging
from typing import Dict, Any
from data_enrichment_metadata import MetadataExtractor
from data_enrichment_context import ContextExtractor
from data_enrichment_external import DataEnrichmentService
from data_enrichment_internal import InternalDataUtility
from utils import load_config as utils_load_config  # Importing load_config from utils.py for type checking

class DataEnrichmentProcessor:
    def __init__(self, config: Dict[str, Any]):
        if not isinstance(config, dict):
            logging.error("Config must be a dictionary.")
            raise ValueError("Config must be a dictionary.")
        self.config = config
        self._metadata_extractor = MetadataExtractor(config)
        self._context_extractor = ContextExtractor(config)
        self._data_enrichment_service = DataEnrichmentService(config)
        self._internal_data_utility = InternalDataUtility(config)

    @staticmethod
    def load_config(_req) -> Dict[str, Any]:
        try:
            config = utils_load_config('config.json')  # Utilizing the load_config from utils.py for consistency and type checking
            if not config:
                logging.error("Config file not found or invalid format.")
                return {}
            return config
        except Exception as e:
            logging.error(f"Failed to load config: {str(e)}")
            return {}

    def enrich_data(self, file_path: str, file_text: str) -> Dict[str, Any]:
        try:
            if not isinstance(file_path, str) or not isinstance(file_text, str):
                raise ValueError("file_path and file_text must be strings.")
            summary = self._metadata_extractor.generate_summary(file_text)
            metadata = self._metadata_extractor.extract_metadata(file_path, file_text, summary)
            context = self._context_extractor.extract_enhanced_context(file_text)
            external_data = self._data_enrichment_service.integrate_external_data(metadata, context)
            internal_data = self._internal_data_utility.prepare_data_for_llm(metadata, context)
            enriched_data = {
                'metadata': metadata,
                'context': context,
                'external_data': external_data,
                'internal_data': internal_data
            }

            return enriched_data
        except Exception as e:
            logging.error(f"Failed to enrich data: {str(e)}")
            return {}

# Tests because it is more convenient to have them in the same file
import unittest
from unittest.mock import patch, MagicMock

class TestDataEnrichmentProcessor(unittest.TestCase):
    def setUp(self):
        self.config = {'key': 'value'}
        self.processor = DataEnrichmentProcessor(self.config)
        self.file_path = "path/to/test/file.txt"
        self.file_text = "This is a test file content."

    @patch('data_enrichment_main.MetadataExtractor')
    @patch('data_enrichment_main.ContextExtractor')
    @patch('data_enrichment_main.DataEnrichmentService')
    @patch('data_enrichment_main.InternalDataUtility')
    def test_enrich_data(self, MockInternalDataUtility, MockDataEnrichmentService, MockContextExtractor, MockMetadataExtractor):
        # Setup mock returns
        MockMetadataExtractor.return_value.extract_metadata.return_value = {'metadata': 'metadata'}
        MockContextExtractor.return_value.extract_enhanced_context.return_value = {'context': 'context'}
        MockDataEnrichmentService.return_value.integrate_external_data.return_value = {'external_data': 'external_data'}
        MockInternalDataUtility.return_value.prepare_data_for_llm.return_value = {'internal_data': 'internal_data'}

        # Execute the method
        enriched_data = self.processor.enrich_data(self.file_path, self.file_text)

        # Assertions
        self.assertIsInstance(enriched_data, dict)
        self.assertIn('metadata', enriched_data)
        self.assertIn('context', enriched_data)
        self.assertIn('external_data', enriched_data)
        self.assertIn('internal_data', enriched_data)

        # Verify interactions
        MockMetadataExtractor.return_value.extract_metadata.assert_called_once_with(self.file_path, self.file_text, None)
        MockContextExtractor.return_value.extract_enhanced_context.assert_called_once_with(self.file_text)
        MockDataEnrichmentService.return_value.integrate_external_data.assert_called_once_with({'metadata': 'metadata'}, {'context': 'context'})
        MockInternalDataUtility.return_value.prepare_data_for_llm.assert_called_once_with({'metadata': 'metadata'}, {'context': 'context'})

if __name__ == '__main__':
    unittest.main()
