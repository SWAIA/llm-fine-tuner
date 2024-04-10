import requests
import logging
from typing import Dict, Any, Optional

class InternalDataUtility:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.internalData: Dict[str, Any] = {}

    def prepareDataForLLM(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepares data for LLM by simulating and extracting relevant data."""
        self._simulateAndExtractData(metadata, context)
        self._handleInternalSources()
        return self.internalData

    def _simulateAndExtractData(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Simulates data extraction based on metadata and context."""
        entities = context.get('named_entities', [])
        keywords = metadata.get('keywords', [])
        for entity in entities:
            self.internalData[entity] = {'entity': entity, 'details': 'Simulated entity details for internal use.'}
        for keyword in keywords:
            self.internalData[keyword] = {'keyword': keyword, 'related_topics': ['Internal Topic 1', 'Internal Topic 2']}

    def _handleInternalSources(self) -> None:
        """Handles data fetching from configured internal sources."""
        internalDataSources = self.config.get('internal_data_sources', {'api_calls': []})
        for source in internalDataSources.get('api_calls', []):
            sourceType = source.get('type')
            if sourceType in self.sourceHandlers:
                self.internalData.update(self.sourceHandlers[sourceType](source))

    @staticmethod
    def _fetchGenericInternalAPIData(source: Dict[str, Any]) -> Dict[str, Any]:
        """Fetches generic API data, handling errors and logging."""
        try:
            response = requests.get(source['url'], params=source.get('params', {}))
            if response.ok:
                return response.json()
            else:
                logging.warning(f"Failed to fetch internal data from {source['url']}, status code: {response.status_code}")
                return {}
        except Exception as e:
            logging.error(f"Error fetching internal data from {source['url']}: {e}")
            return {}

    sourceHandlers: Dict[str, Any] = {
        'notion': lambda self, source: self._fetchInternalDataFromNotion(source),
        'google': lambda self, source: self._fetchInternalDataFromGoogle(source),
        'openai': lambda self, source: self._fetchInternalDataFromOpenAI(source),
        'hugging_face': lambda self, source: self._fetchInternalDataFromHuggingFace(source),
        'generic': _fetchGenericInternalAPIData
    }

    @staticmethod
    def _make_api_request(url: str, params: Optional[Dict[str, Any]] = None, method: str = 'GET', headers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generalized API request function, handling method, headers, and parameters."""
        try:
            response = getattr(requests, method.lower())(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logging.warning(f"API request to {url} failed with status code {response.status_code}")
                return {}
        except Exception as e:
            logging.error(f"Error making API request to {url}: {e}")
            return {}

    def _fetchInternalDataFromNotion(self, source: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Notion-Version": "2022-06-28"}
        return self._make_api_request(source['url'], headers=headers)

    def _fetchInternalDataFromGoogle(self, source: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_api_request(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": source.get('api_key', ''),
                "cx": source.get('cx', ''),
                "q": source.get('query', '')
            }
        )

    def _fetchInternalDataFromOpenAI(self, source: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_api_request(
            "https://api.openai.com/v1/answers",
            method='POST',
            headers={
                "Authorization": f"Bearer {source.get('api_key', '')}",
                "Content-Type": "application/json"
            },
            params={
                "model": source.get('model', "text-davinci-003"),
                "question": source.get('question', ''),
                "documents": source.get('documents', []),
                "examples_context": source.get('examples_context', ''),
                "examples": source.get('examples', []),
                "max_tokens": source.get('max_tokens', 100),
                "stop": source.get('stop', ["\n", "\n\n"]),
            }
        )

    def _fetchInternalDataFromHuggingFace(self, source: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {source.get('api_key', '')}"}
        payload = {
            "inputs": source.get('inputs'),
            "parameters": {
                "min_length": source.get('min_length', 0),
                "max_length": source.get('max_length', 512),
                "top_k": source.get('top_k', 50),
                "top_p": source.get('top_p', 0.95),
                "temperature": source.get('temperature', 1.0),
                "repetition_penalty": source.get('repetition_penalty', 1.0),
                "max_time": source.get('max_time', 1.0),
                "max_new_tokens": source.get('max_new_tokens', 512),
                "return_full_text": source.get('return_full_text', True),
                "num_return_sequences": source.get('num_return_sequences', 1),
                "do_sample": source.get('do_sample', True)
            },
            "options": {
                "use_cache": source.get('use_cache', True),
                "wait_for_model": source.get('wait_for_model', False)
            }
        }
        return self._make_api_request(source['url'], method='POST', headers=headers, params=payload)

# Tests because it is more convenient to have them in the same file
import unittest
from unittest.mock import patch, MagicMock

class TestInternalDataUtility(unittest.TestCase):
    def setUp(self):
        self.config = {'api_key': 'test_api_key', 'model': 'text-davinci-003', 'url': 'https://api.huggingface.co'}
        self.internal_data_utility = InternalDataUtility(self.config)
        self.source = {
            'api_key': 'test_api_key',
            'inputs': 'What is the meaning of life?',
            'min_length': 0,
            'max_length': 512,
            'top_k': 50,
            'top_p': 0.95,
            'temperature': 1.0,
            'repetition_penalty': 1.0,
            'max_time': 1.0,
            'max_new_tokens': 512,
            'return_full_text': True,
            'num_return_sequences': 1,
            'do_sample': True,
            'url': 'https://api.huggingface.co'
        }

    @patch('data_enrichment_internal.requests')
    def test_fetchInternalDataFromHuggingFace(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {'answer': '42'}
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        response = self.internal_data_utility._fetchInternalDataFromHuggingFace(self.source)
        self.assertEqual(response, {'answer': '42'})

        mock_requests.post.assert_called_once_with(
            'https://api.huggingface.co',
            headers={"Authorization": "Bearer test_api_key"},
            params={
                "inputs": "What is the meaning of life?",
                "parameters": {
                    "min_length": 0,
                    "max_length": 512,
                    "top_k": 50,
                    "top_p": 0.95,
                    "temperature": 1.0,
                    "repetition_penalty": 1.0,
                    "max_time": 1.0,
                    "max_new_tokens": 512,
                    "return_full_text": True,
                    "num_return_sequences": 1,
                    "do_sample": True
                },
                "options": {
                    "use_cache": True,
                    "wait_for_model": False
                }
            }
        )

    @patch('data_enrichment_internal.requests')
    def test_make_api_request_get_method(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response

        response = self.internal_data_utility._make_api_request('https://api.test.com', method='GET')
        self.assertEqual(response, {'data': 'test_data'})

        mock_requests.get.assert_called_once_with('https://api.test.com', params=None, headers=None)

    @patch('data_enrichment_internal.requests')
    def test_make_api_request_post_method(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        response = self.internal_data_utility._make_api_request('https://api.test.com', params={'key': 'value'}, method='POST', headers={'Authorization': 'Bearer test'})
        self.assertEqual(response, {'data': 'test_data'})

        mock_requests.post.assert_called_once_with('https://api.test.com', params={'key': 'value'}, headers={'Authorization': 'Bearer test'})

if __name__ == '__main__':
    unittest.main()
