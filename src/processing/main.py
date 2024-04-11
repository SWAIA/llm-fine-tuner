import asyncio
from typing import Dict, Any
from ..utils import Utils

from src.processing.metadata_extractor import MetadataExtractor
from src.processing.context_extractor import ContextExtractor
from src.processing.data_processor import ExternalDataProcessor
from src.processing.file_processor import InternalFileProcessor

class DataProcessor:

    def __init__(self, config: Dict[str, Any], output_file: str):
        self.config = config
        self.output_file = output_file
        self.initialize_services()

    def initialize_services(self):
        self.metadata_extractor = MetadataExtractor(self.config)
        self.context_extractor = ContextExtractor(self.config)
        self.data_enrichment_service = ExternalDataProcessor(self.config)
        self.internal_data_utility = InternalFileProcessor(self.config)

    async def process_files(self, input_dir: str):
        Utils.log_info("Starting file processing")
        file_paths = await self._traverse_directories(input_dir)
        all_data = await self._process_all_files(file_paths)
        await self._save_processed_data(all_data)
        Utils.log_info("File processing completed")

    async def _traverse_directories(self, input_dir: str):
        return await Utils.traverse_directories(input_dir)
    
    async def _process_all_files(self, file_paths):
        all_data = await self._gather_file_data(file_paths)
        return all_data

    async def _gather_file_data(self, file_paths):
        all_data = []
        tasks = [self._process_file(file_path) for file_path in file_paths if Utils.is_supported_file(file_path)]
        await asyncio.gather(*tasks, return_exceptions=True)
        return all_data

    async def _process_file(self, file_path):
        try:
            file_text = await Utils.extract_text(file_path)
            enriched_data = self._enrich_data(file_path, file_text)
            enriched_data['metadata'] = {'file_path': file_path}
            self.all_data.append(enriched_data)
        except Exception as e:
            Utils.log_error(f"Error processing file {file_path}: {e}")

    async def _save_processed_data(self, all_data):
        await Utils.save_structured_data(all_data, self.output_file)

    def _enrich_data(self, file_path: str, file_text: str) -> Dict[str, Any]:
        try:
            assert isinstance(file_path, str) and isinstance(file_text, str), "file_path and file_text must be strings."
            summary = self.metadata_extractor.generate_summary(file_text)
            metadata = self.metadata_extractor.extract_metadata(file_path, file_text, summary)
            context = self.context_extractor.extract_enhanced_context(file_text)
            external_data = self.data_enrichment_service.integrate_external_data(metadata, context)
            internal_data = self.internal_data_utility.prepare_data_for_llm(metadata, context)
            
            enriched_data = {
                'metadata': metadata,
                'context': context,
                'external_data': external_data,
                'internal_data': internal_data
            }
            
            return enriched_data
        except AssertionError as e:
            Utils.log_error(f"Assertion error during data enrichment: {e}")
        except Exception as e:
            Utils.log_error(f"Failed to enrich data: {str(e)}")
        return {}
