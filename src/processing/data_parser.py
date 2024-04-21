from typing import Dict
from ..utils import LoggerService, RequestManager, ConfigManager



class DataProcessor:
    def __init__(self, config: Dict[str, Dict]):
        self.config = config
        self.external_data: Dict[str, Dict] = {}
        self.cache: Dict[str, Dict] = {}
        self.source_fetchers: Dict[str, callable] = {
            'generic': self._fetch_generic_api_data,
        }
        self.logger = LoggerService.get_instance()
        self.config_manager = ConfigManager()
        self.request_manager = RequestManager(self.logger)

    async def integrate_external_data(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> Dict[str, Dict]:
        await self._extract_and_simulate_data(metadata, context)
        await self._process_external_sources()
        return self.external_data

    async def _extract_and_simulate_data(self, metadata: Dict[str, Dict], context: Dict[str, Dict]) -> None:
        for entity in context.get('named_entities', []): 
            self.external_data[entity] = {'entity': entity, 'details': 'Simulated entity details from external source.'}
        for keyword in metadata.get('keywords', []): 
            self.external_data[keyword] = {'keyword': keyword, 'related_topics': ['Topic 1', 'Topic 2']}

    async def _process_external_sources(self) -> None:
        external_data_sources = self.config.get('external_data_sources', {}).get('api_calls', [])
        for source in external_data_sources:
            if fetcher := self.source_fetchers.get(source.get('type')):
                self.external_data.update(await fetcher(source))

    async def _fetch_generic_api_data(self, source: Dict[str, Dict]) -> Dict[str, Dict]:
        cache_key = source['url'] + str(source.get('params', {}))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        response = await self.request_manager.send_request(source['url'], params=source.get('params', {}))
        if 'status' in response and response['status'] == 'ok':
            self.cache[cache_key] = response
            return self.cache[cache_key]
        else:
            await self.logger.log("error", f"Failed to fetch data from {source['url']}")
            return {}
    
    async def _initialize_models_and_pipelines(self) -> Dict[str, str]:
        try:
            return await self.config_manager.get_models_and_pipelines(self.config)
        except Exception as e:
            await self.logger.log("error", f"Error initializing models and pipelines: {e}")
            return {}

    async def _get_config_value(self, section: str, key: str, default: str) -> str:
        try:
            return await self.config_manager.load_config().get(section, {}).get(key, default)
        except Exception as e:
            await self.logger.log("error", f"Error accessing config value for section {section} and key {key}: {e}")
            return default
