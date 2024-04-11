import asyncio
from typing import Dict, Any
from ..utils import UtilityFunctions as Utils

from src.processing.metadata_extractor import MetadataExtractor
from src.processing.context_extractor import ContextExtractor
from src.processing.data_processor import DataProcessor
from src.processing.file_processor import FileProcessor

class DataProcessor:

    def __init__(self, config: Dict[str, Any], output_file: str):
        self.config = config
        self.output_file = output_file
        self.utils = Utils.get_instance()  # Utilize the singleton pattern for utility functions
        self.initialize_services()

    def initialize_services(self):
        self.metadata_extractor = MetadataExtractor(self.config)
        self.context_extractor = ContextExtractor(self.config)
        self.data_enrichment_service = DataProcessor(self.config)
        self.internal_data_utility = FileProcessor(self.config)

    async def process_files(self, input_dir: str):
        self.utils.log_info("Starting file processing")
        file_paths = self.utils.list_files_in_directory(input_dir)  # Directly use the utility function
        all_data = await self._process_all_files(file_paths)
        
        self.utils.save_data_to_file(all_data, self.output_file)  # Directly use the utility function
        self.utils.log_info("File processing completed")

    async def _enrich_data(self, file_path: str, file_text: str) -> Dict[str, Any]:
        summary = await self.metadata_extractor.generate_summary(file_text)
        metadata = await self.metadata_extractor.extract_metadata(file_path, file_text, summary)
        context = await self.context_extractor.extract_enhanced_context(file_text)
        external_data = await self.data_enrichment_service.integrate_external_data(metadata, context)
        internal_data = await self.internal_data_utility.prepare_data_for_llm(metadata, context)

        enriched_data = {
            'metadata': metadata,
            'context': context,
            'external_data': external_data,
            'internal_data': internal_data
        }

        return enriched_data

