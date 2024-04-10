import requests
import logging
from typing import Dict

class DataEnrichmentService:
    def __init__(self, config: Dict[str, Dict]):
        if not isinstance(config, dict): 
            raise ValueError("Config must be a dictionary.")
        self.config = config
        self.external_data: Dict[str, Dict] = {}
        self.cache = {}

    integrate_external_data = lambda self, metadata: Dict[str, Dict], context: Dict[str, Dict]: self._integrate_external_data(metadata, context)

    def _integrate_external_data(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> Dict[str, Dict]:
        if not isinstance(metadata, dict) or not isinstance(context, dict): 
            raise TypeError("Metadata and context must be dictionaries.")
        self._extract_and_simulate_data(metadata, context)
        self._process_external_sources()
        return self.external_data

    # Simulates data retrieval based on entities and keywords
    def _extract_and_simulate_data(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> None:
        entities = context.get('named_entities', [])
        keywords = metadata.get('keywords', [])
        for entity in entities: 
            self.external_data[entity] = {'entity': entity, 'details': 'Simulated entity details from external source.'}
        for keyword in keywords: 
            self.external_data[keyword] = {'keyword': keyword, 'related_topics': ['Topic 1', 'Topic 2']}

    # Processes data from external sources as defined in the configuration
    def _process_external_sources(self) -> None:
        external_data_sources = self.config.get('external_data_sources', {'api_calls': []})
        for source in external_data_sources.get('api_calls', []):
            source_type = source.get('type')
            if source_type in self.source_fetchers: 
                self.external_data.update(self.source_fetchers[source_type](source))

    # Maps source types to their respective fetcher functions
    source_fetchers: Dict[str, Dict] = {
        'notion': lambda source: self._fetch_data_from_notion(source),
        'google': lambda source: self._fetch_data_from_google(source),
        'openai': lambda source: self._fetch_data_from_openai(source),
        'hugging_face': lambda source: self._fetch_data_from_hugging_face(source),
        'generic': lambda source: self._fetch_generic_api_data(source)
    }

    # Fetches data from generic APIs
    def _fetch_generic_api_data(self, source: Dict[str, Dict]) -> Dict[str, Dict]:
        cache_key = source['url'] + str(source.get('params', {}))
        if cache_key in self.cache:
            return self.cache[cache_key]
        try:
            response = requests.get(source['url'], params=source.get('params', {}))
            result = response.json() if response.ok else logging.warning(f"Failed to fetch data from {source['url']}, status code: {response.status_code}") or {}
            self.cache[cache_key] = result
            return result
        except Exception as e: 
            logging.error(f"Error fetching data from {source['url']}: {e}")
            return {}

    # Fetchers for specific sources, utilizing a common method for API requests where applicable
    def _fetch_data_from_notion(self, source: Dict[str, Dict]) -> Dict[str, Dict]:
        headers = {"Notion-Version": self.config.get('notion_version', "2022-06-28")}
        return self._make_api_request(source['url'], headers=headers)

    def _fetch_data_from_google(self, source: Dict[str, Dict]) -> Dict[str, Dict]:
        try:
            response = requests.get("https://www.googleapis.com/customsearch/v1", params={"key": source.get('api_key', self.config.get('api_keys', {}).get('google_api_key', '')), "cx": source.get('cx', self.config.get('defaults', {}).get('cx', '')), "q": source.get('query', self.config.get('defaults', {}).get('query', ''))})
            return response.json() if response.status_code == 200 else {}
        except Exception: 
            return {}

    def _fetch_data_from_openai(self, source: Dict[str, Dict]) -> Dict[str, Dict]:
        try:
            response = requests.post("https://api.openai.com/v1/answers", headers={"Authorization": f"Bearer {source.get('api_key', self.config.get('api_keys', {}).get('openai_api_key', ''))}", "Content-Type": "application/json"}, json={"model": source.get('model', self.config.get('defaults', {}).get('model', "text-davinci-003")), "question": source.get('question', self.config.get('defaults', {}).get('question', '')), "documents": source.get('documents', self.config.get('defaults', {}).get('documents', [])), "examples_context": source.get('examples_context', self.config.get('defaults', {}).get('examples_context', '')), "examples": source.get('examples', self.config.get('defaults', {}).get('examples', [])), "max_tokens": source.get('max_tokens', self.config.get('defaults', {}).get('max_tokens', 100)), "stop": source.get('stop', self.config.get('defaults', {}).get('stop', ["\n", "\n\n"]))})
            return response.json() if response.status_code == 200 else {}
        except Exception: 
            return {}

    def _fetch_data_from_hugging_face(self, source: Dict[str, Dict]) -> Dict[str, Dict]:
        try:
            headers = {"Authorization": f"Bearer {source.get('api_key', self.config.get('api_keys', {}).get('hugging_face_api_key', ''))}"}
            payload = {"inputs": source.get('inputs', self.config.get('defaults', {}).get('inputs', '')), "parameters": source.get('parameters', self.config.get('defaults', {}).get('parameters', {})), "options": source.get('options', self.config.get('defaults', {}).get('options', {}))}
            return self._make_api_request(source['url'], method='POST', headers=headers, json=payload)
        except Exception: 
            return {}

    # General method for making API requests
    def _make_api_request(self, url, method='GET', headers=None, json=None):
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            else:
                response = requests.post(url, headers=headers, json=json)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logging.error(f"Error making API request to {url}: {e}")
            return {}

# Tests because it is more convienient to have them in the same file
import unittest
from unittest.mock import patch, MagicMock

class TestDataEnrichmentExternal(unittest.TestCase):
    def setUp(self):
        self.config = {'api_keys': {'google_api_key': 'test_google_api_key', 'openai_api_key': 'test_openai_api_key', 'hugging_face_api_key': 'test_hugging_face_api_key'}, 'defaults': {'cx': 'test_cx', 'query': 'test_query', 'model': 'text-davinci-003', 'question': 'test_question', 'documents': [], 'examples_context': 'test_examples_context', 'examples': [], 'max_tokens': 100, 'stop': ["\n", "\n\n"], 'inputs': 'test_inputs', 'parameters': {}, 'options': {}}}
        self.data_enrichment_service = DataEnrichmentService(self.config)

    @patch('data_enrichment_external.requests.get')
    def test_fetch_data_from_google(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'items': ['test_item']}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        source = {'api_key': 'override_key', 'cx': 'override_cx', 'query': 'override_query'}
        result = self.data_enrichment_service._fetch_data_from_google(source)
        self.assertEqual(result, {'items': ['test_item']})

        mock_get.assert_called_once_with("https://www.googleapis.com/customsearch/v1", params={"key": "override_key", "cx": "override_cx", "q": "override_query"})

    @patch('data_enrichment_external.requests.post')
    def test_fetch_data_from_openai(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'answers': ['test_answer']}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        source = {'api_key': 'override_key', 'inputs': 'override_inputs', 'parameters': {'temperature': 0.7}, 'options': {'wait_for_model': True}}
        result = self.data_enrichment_service._fetch_data_from_openai(source)
        self.assertEqual(result, {'answers': ['test_answer']})

        expected_payload = {
            "inputs": "override_inputs",
            "parameters": {"temperature": 0.7},
            "options": {"wait_for_model": True}
        }
        mock_post.assert_called_once_with(
            "https://api.openai.com/v1/completions",
            headers={"Authorization": "Bearer override_key"},
            json=expected_payload
        )

    @patch('data_enrichment_external.requests.get')
    def test_fetch_generic_api_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        source = {'url': 'https://genericapi.com/data', 'params': {'key': 'generic_key', 'query': 'generic_query'}}
        result = self.data_enrichment_service._fetch_generic_api_data(source)
        self.assertEqual(result, {'data': 'test_data'})

        mock_get.assert_called_once_with(
            "https://genericapi.com/data",
        