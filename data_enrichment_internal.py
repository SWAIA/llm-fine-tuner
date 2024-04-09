import requests
import logging

class InternalDataUtility:
    def __init__(self, config):
        self.config = config
        self.internalData = {}

    # Prepares data for LLM by simulating and extracting relevant data.
    def prepareDataForLLM(self, metadata, context):
        self._simulateAndExtractData(metadata, context)
        self._handleInternalSources()
        return self.internalData

    # Simulates data extraction based on metadata and context.
    def _simulateAndExtractData(self, metadata, context):
        entities = context.get('named_entities', [])
        keywords = metadata.get('keywords', [])
        for entity in entities:
            self.internalData[entity] = {'entity': entity, 'details': 'Simulated entity details for internal use.'}
        for keyword in keywords:
            self.internalData[keyword] = {'keyword': keyword, 'related_topics': ['Internal Topic 1', 'Internal Topic 2']}

    # Handles data fetching from configured internal sources.
    def _handleInternalSources(self):
        internalDataSources = self.config.get('internal_data_sources', {'api_calls': []})
        for source in internalDataSources.get('api_calls', []):
            sourceType = source.get('type')
            if sourceType in self.sourceHandlers:
                self.internalData.update(self.sourceHandlers[sourceType](source))

    # Maps source types to their respective handler functions.
    sourceHandlers = {
        'notion': lambda self, source: self._fetchInternalDataFromNotion(source),
        'google': lambda self, source: self._fetchInternalDataFromGoogle(source),
        'openai': lambda self, source: self._fetchInternalDataFromOpenAI(source),
        'hugging_face': lambda self, source: self._fetchInternalDataFromHuggingFace(source),
        'generic': lambda self, source: self._fetchGenericInternalAPIData(source)
    }

    # Fetches generic API data, handling errors and logging.
    def _fetchGenericInternalAPIData(self, source):
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

    # Fetches data from Notion using specific headers.
    def _fetchInternalDataFromNotion(self, source):
        headers = {"Notion-Version": "2022-06-28"}
        return self._makeInternalAPIRequest(source['url'], headers=headers)

    # Fetches data from Google Custom Search API.
    def _fetchInternalDataFromGoogle(self, source):
        return self._make_api_request(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": source.get('api_key', ''),
                "cx": source.get('cx', ''),
                "q": source.get('query', '')
            }
        )

    # Fetches data from OpenAI API.
    def _fetchInternalDataFromOpenAI(self, source):
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

    # Fetches data from Hugging Face API.
    def _fetchInternalDataFromHuggingFace(self, source):
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

    # Generalized API request function, handling method, headers, and parameters.
    def _make_api_request(self, url, params=None, method='GET', headers=None):
        try:
            response = getattr(requests, method.lower())(url, params=params, headers=headers)
            return response.json() if response.status_code == 200 else {}
        except Exception:
            return {}

