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
            raise ValueError("Config must be a dictionary.")
        self.config = config
        self._metadata_extractor = MetadataExtractor(config)
        self._context_extractor = ContextExtractor(config)
        self._data_enrichment_service = DataEnrichmentService(config)
        self._internal_data_utility = InternalDataUtility(config)

    @staticmethod
    def load_config(_req) -> Dict[str, Any]:
        config = utils_load_config('config.json')  # Utilizing the load_config from utils.py for consistency and type checking
        if not config:
            logging.error("Config file not found or invalid format.")
        return config

    def enrich_data(self, file_path: str, file_text: str) -> Dict[str, Any]:
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

