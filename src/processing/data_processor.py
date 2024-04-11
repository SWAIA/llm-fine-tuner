from typing import Dict
from ..utils import Utils

class DataProcessor:
    
    def __init__(self, config: Dict[str, Dict]):
        self.config = config
        self.external_data: Dict[str, Dict] = Utils.external_data
        self.cache: Dict[str, Dict] = Utils.cache
        self.source_fetchers: Dict[str, callable] = {
            'generic': self._fetch_generic_api_data,
        }

    def integrate_external_data(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> Dict[str, Dict]:
        self._extract_and_simulate_data(metadata, context)
        self._process_external_sources()
        return self.external_data

    def _extract_and_simulate_data(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> None:
        for entity in context.get('named_entities', []): 
            self.external_data[entity] = {'entity': entity, 'details': 'Simulated entity details from external source.'}
        for keyword in metadata.get('keywords', []): 
            self.external_data[keyword] = {'keyword': keyword, 'related_topics': ['Topic 1', 'Topic 2']}

    def _process_external_sources(self) -> None:
        external_data_sources = self.config.get('external_data_sources', {}).get('api_calls', [])
        for source in external_data_sources:
            fetcher = self.source_fetchers.get(source.get('type'))
            if fetcher:
                self.external_data.update(fetcher(source))

    def _fetch_generic_api_data(self, source: Dict[str, Dict]) -> Dict[str, Dict]:
        cache_key = source['url'] + str(source.get('params', {}))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        response = Utils.make_api_request(source['url'], params=source.get('params', {}))
        if response.ok:
            self.cache[cache_key] = response.json()
            return self.cache[cache_key]
        else:
            Utils.log_error(f"Failed to fetch data from {source['url']}, status code: {response.status_code}")
            return {}
    
    def _initialize_models_and_pipelines(self) -> Dict[str, str]:
        try:
            models_and_pipelines = Utils.get_models_and_pipelines(self.config)
            return models_and_pipelines
        except Exception as e:
            Utils.log_error(f"Error initializing models and pipelines: {e}")
            return {}

    def _get_config_value(self, section: str, key: str, default: str) -> str:
        try:
            return Utils.load_config(self.config).get(section, {}).get(key, default)
        except Exception as e:
            Utils.log_error(f"Error accessing config value for section {section} and key {key}: {e}")
            return default
