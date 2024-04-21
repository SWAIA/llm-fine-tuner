from typing import Dict, Any
import asyncio

from src.utils import LoggerService

class DataProcessor:

    def __init__(self, config: Dict[str, Any], output_file: str):
        self.config = config
        self.output_file = output_file
        # Utilize the singleton pattern for logging
        self.logger = LoggerService("DataProcessorLogger")
        # Utilize the FileManager for file operations
        # self.file_manager = "FileManager()"
        # self.initialize_services()
        self.logger.log("info", "DataProcessor initialized")

    def initialize_services(self):
        from src.processing.metadata_extractor import MetadataExtractor
        from src.processing.context_extractor import ContextExtractor
        from processing.file_crawler import FileProcessor

        self.metadata_extractor = MetadataExtractor(self.config)
        self.context_extractor = ContextExtractor(self.config)
        # self.data_enrichment_service = DataProcessor(self.config)
        self.internal_data_utility = FileProcessor(self.config)

    def process_files(self, input_dir: str):
        async def process_files_async():
            await self.logger.log("info", "Starting file processing")
            # Use FileManager to list files
            file_paths = self.file_manager.find_files(input_dir)
            all_data = await self._process_all_files(file_paths)
            
            # Use FileManager to save data
            await self.file_manager.save_data_to_file(all_data, self.output_file)
            await self.logger.log("info", "File processing completed")
        
        asyncio.run(process_files_async())

    async def _enrich_data(self, file_path: str, file_text: str) -> Dict[str, Any]:
        # Check if processing steps are enabled in the config
        process_metadata = self.config.get('process_metadata', True)
        process_context = self.config.get('process_context', True)
        process_external_data = self.config.get('process_external_data', True)
        process_internal_data = self.config.get('process_internal_data', True)

        summary = ""
        metadata = {}
        context = {}
        external_data = {}
        internal_data = {}

        if process_metadata:
            summary = await self.metadata_extractor.generate_summary(file_text)
            metadata = await self.metadata_extractor.extract_metadata(file_path, file_text, summary)
        
        if process_context:
            context = await self.context_extractor.extract_enhanced_context(file_text)
        
        if process_external_data:
            # Assuming a correct service is instantiated for data_enrichment_service, the following line is corrected.
            external_data = await self.data_enrichment_service.integrate_external_data(metadata, context)
        
        if process_internal_data:
            internal_data = await self.internal_data_utility.prepare_data_for_llm(metadata, context)

        return {
            'metadata': metadata,
            'context': context,
            'external_data': external_data,
            'internal_data': internal_data,
        }

