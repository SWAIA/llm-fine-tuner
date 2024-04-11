from typing import Dict, List
from utils import Utilities as Utils
from requests.exceptions import RequestException
from zipfile import ZipFile
import os

class FileProcessor:
    def __init__(self, config: Dict[str, Dict]):
        self.config = config
        self.internal_data: Dict[str, Dict] = {}
        self.source_handlers = {handler_type: getattr(self, f"_fetch_{handler_type}_internal_api_data")
                                 for handler_type in config.get('internal_data_source_types', ['generic'])}
        self.error_count = 0

    def _fetch_generic_internal_api_data(self, source: Dict[str, Dict]) -> Dict[str, Dict]:
        try:
            response = Utils.make_api_request(source.get('url'), params=source.get('params', {}), headers=source.get('headers', {}))
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            self.error_count += 1
            Utils.log_error(f"Failed to fetch internal data from {source.get('url')}, error: {e}")
            return {}

    def prepare_data_for_llm(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> Dict[str, Dict]:
        self._simulate_and_extract_data(metadata, context)
        self._handle_internal_sources()
        return self.internal_data

    def _simulate_and_extract_data(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> None:
        entities = context.get('named_entities', [])
        keywords = metadata.get('keywords', [])
        
        self.internal_data = {
            entity: {'entity': entity, 'details': 'Simulated entity details for internal use.'}
            for entity in entities
        }
        self.internal_data.update({
            keyword: {'keyword': keyword, 'related_topics': ['Internal Topic 1', 'Internal Topic 2']}
            for keyword in keywords
        })

    def _handle_internal_sources(self) -> None:
        internal_data_sources = self.config.get('internal_data_sources', [])
        for source in internal_data_sources:
            handler = self.source_handlers.get(source.get('type'))
            if handler:
                self.internal_data.update(handler(source))

    def process_zip_file(self, zip_path: str, extract_dir: str) -> Dict[str, str]:
        os.makedirs(extract_dir, exist_ok=True)
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        extracted_files = [os.path.relpath(os.path.join(root, name), extract_dir) for root, dirs, files in os.walk(extract_dir, topdown=True) for name in files if not name.startswith('.')]
        return extracted_files

    def read_python_files(self, file_paths: List[str], extract_dir: str) -> Dict[str, str]:
        file_contents = {}
        for file_path in file_paths:
            if file_path.endswith('.py'):  # Process only Python files
                with open(os.path.join(extract_dir, file_path), 'r') as file:
                    file_contents[file_path] = file.read()
        return file_contents

    def display_utils_content(self, python_file_contents: Dict[str, str]) -> None:
        utils_content = python_file_contents['src/utils.py']
        print(utils_content)

    def read_test_content(self, test_content_path: str) -> str:
        with open(test_content_path, 'r') as file:
            test_content = file.read()
        return test_content

    def process_files(self, zip_path: str, extract_dir: str, test_content_path: str) -> Dict[str, str]:
        extracted_files = self.process_zip_file(zip_path, extract_dir)
        python_files = [file for file in extracted_files if file.endswith('.py')]
        python_file_contents = self.read_python_files(python_files)
        self.display_utils_content(python_file_contents)
        test_content = self.read_test_content(test_content_path)

        return {
            'extracted_files': extracted_files,
            'python_files': python_files,
            'python_file_contents': python_file_contents,
            'test_content': test_content
        }
