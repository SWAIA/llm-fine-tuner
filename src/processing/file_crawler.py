from typing import Dict, List
import os

class FileProcessor:
    def __init__(self, config: Dict[str, Dict]):
        from src.utils import LoggerService, FileManager, RequestManager
        self.config = config
        self.internal_data: Dict[str, Dict] = {}
        self.logger = LoggerService.get_instance("FileProcessorLogger")
        self.request_manager = RequestManager(self.logger)
        self.file_manager = FileManager()
        self.source_handlers = {handler_type: getattr(self, f"_fetch_{handler_type}_internal_api_data")
                                 for handler_type in config.get('internal_data_source_types', ['generic'])}
        self.error_count = 0

    async def _fetch_generic_internal_api_data(self, source: Dict[str, Dict]) -> Dict[str, Dict]:
        try:
            return await self.request_manager.send_request(
                source.get('url'),
                params=source.get('params', {}),
                headers=source.get('headers', {}),
            )
        except Exception as e:
            self.error_count += 1
            await self.logger.log("error", f"Failed to fetch internal data from {source.get('url')}, error: {e}")
            return {}

    async def prepare_data_for_llm(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> Dict[str, Dict]:
        await self._simulate_and_extract_data(metadata, context)
        await self._handle_internal_sources()
        return self.internal_data

    async def _simulate_and_extract_data(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> None:
        entities = context.get('named_entities', [])
        keywords = metadata.get('keywords', [])

        self.internal_data = {
            entity: {
                'entity': entity,
                'details': 'Simulated entity details for internal use.',
            }
            for entity in entities
        } | {
            keyword: {
                'keyword': keyword,
                'related_topics': ['Internal Topic 1', 'Internal Topic 2'],
            }
            for keyword in keywords
        }

    async def _handle_internal_sources(self) -> None:
        internal_data_sources = self.config.get('internal_data_sources', [])
        for source in internal_data_sources:
            if handler := self.source_handlers.get(source.get('type')):
                self.internal_data.update(await handler(source))

    async def process_zip_file(self, zip_path: str, extract_dir: str) -> Dict[str, str]:
        await self.file_manager.create_directory(extract_dir)
        await self.file_manager.extract_zip_file(zip_path, extract_dir)
        return await self.file_manager.list_files_in_directory(
            extract_dir, exclude_hidden=True
        )

    async def read_python_files(self, file_paths: List[str], extract_dir: str) -> Dict[str, str]:
        file_contents = {}
        for file_path in file_paths:
            if file_path.endswith('.py'):  # Process only Python files
                content = await self.file_manager.read_file(os.path.join(extract_dir, file_path))
                file_contents[file_path] = content
        return file_contents

    async def display_utils_content(self, python_file_contents: Dict[str, str]) -> None:
        utils_content = python_file_contents['src/utils.py']
        print(utils_content)

    async def read_test_content(self, test_content_path: str) -> str:
        return await self.file_manager.read_file(test_content_path)

    async def process_files(self, zip_path: str, extract_dir: str, test_content_path: str) -> Dict[str, str]:
        extracted_files = await self.process_zip_file(zip_path, extract_dir)
        python_files = [file for file in extracted_files if file.endswith('.py')]
        python_file_contents = await self.read_python_files(python_files, extract_dir)
        await self.display_utils_content(python_file_contents)
        test_content = await self.read_test_content(test_content_path)

        return {
            'extracted_files': extracted_files,
            'python_files': python_files,
            'python_file_contents': python_file_contents,
            'test_content': test_content
        }

