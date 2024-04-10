import requests
import logging
from typing import Dict, Optional

class DataEnrichmentService:
    def __init__(self, config: Dict[str, Dict]):
        if not isinstance(config, dict): 
            raise ValueError("Config must be a dictionary.")
        self.config = config
        self.external_data: Dict[str, Dict] = {}
        self.cache = {}

    def integrate_external_data(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> Dict[str, Dict]:
        if not isinstance(metadata, dict) or not isinstance(context, dict): 
            raise TypeError("Metadata and context must be dictionaries.")
        self._extract_and_simulate_data(metadata, context)
        self._process_external_sources()
        return self.external_data

    def _extract_and_simulate_data(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> None:
        entities = context.get('named_entities', [])
        keywords = metadata.get('keywords', [])
        for entity in entities: 
            self.external_data[entity] = {'entity': entity, 'details': 'Simulated entity details from external source.'}
        for keyword in keywords: 
            self.external_data[keyword] = {'keyword': keyword, 'related_topics': ['Topic 1', 'Topic 2']}

    def _process_external_sources(self) -> None:
        external_data_sources = self.config.get('external_data_sources', {'api_calls': []})
        for source in external_data_sources.get('api_calls', []):
            source_type = source.get('type')
            if source_type in self.source_fetchers: 
                self.external_data.update(self.source_fetchers[source_type](source))

    source_fetchers: Dict[str, Dict] = {
        'notion': lambda source: self._fetch_data_from_notion(source),
        'google': lambda source: self._fetch_data_from_google(source),
        'openai': lambda source: self._fetch_data_from_openai(source),
        'hugging_face': lambda source: self._fetch_data_from_hugging_face(source),
        'generic': lambda source: self._fetch_generic_api_data(source)
    }

    def _fetch_generic_api_data(self, source: Dict[str, Dict]) -> Dict[str, Dict]:
        cache_key = source['url'] + str(source.get('params', {}))
        if cache_key in self.cache:
            return self.cache[cache_key]
        try:
            response = requests.get(source['url'], params=source.get('params', {}))
            if response.ok:
                result = response.json()
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
    @staticmethod
    def _fetch_data_from_hugging_face(source: Dict[str, Any]) -> Dict[str, Any]:
        try:
            headers = {"Authorization": f"Bearer {source.get('api_key', DataEnrichmentService._get_config_value('api_keys', 'hugging_face_api_key', ''))}"}
            payload = {
                "inputs": source.get('inputs', DataEnrichmentService._get_config_value('defaults', 'inputs', '')),
                "parameters": source.get('parameters', DataEnrichmentService._get_config_value('defaults', 'parameters', {})),
                "options": source.get('options', DataEnrichmentService._get_config_value('defaults', 'options', {}))
            }
            return DataEnrichmentService._make_api_request(source['url'], method='POST', headers=headers, json=payload)
        except Exception as e: 
            logging.error(f"Error fetching data from Hugging Face API: {e}")
            return {}

    @staticmethod
    def _make_api_request(url: str, method: str = 'GET', headers: Optional[Dict[str, str]] = None, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            else:
                response = requests.post(url, headers=headers, json=json)
            if response.status_code == 200:
                return response.json()
            else:
                logging.warning(f"API request to {url} failed with status code {response.status_code}")
                return {}
        except Exception as e:
            logging.error(f"Error making API request to {url}: {e}")
            return {}

    @staticmethod
    def _get_config_value(section: str, key: str, default: Any) -> Any:
        try:
            return DataEnrichmentService.config.get(section, {}).get(key, default)
        except AttributeError:
            logging.error("Config attribute not set in DataEnrichmentService.")
            return default
