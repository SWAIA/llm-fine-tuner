from typing import List, Dict, Optional
import os
import re
import json
import logging
import subprocess
import requests
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline, set_seed

# Singleton pattern for Utilities class
class _PrivateUtils:
    __utils_instance = None

    @classmethod
    def get_instance(cls, config_path: str = 'config.json') -> 'Utilities':
        if cls.__utils_instance is None:
            cls.__utils_instance = Utilities(config_path)
        return cls.__utils_instance

# Updated utility class with modern Python practices
class Utilities:

    def __init__(self, config_path: str = 'config.json') -> None:
        self.config = self.load_config(config_path)
        self.models = self.init_models(self.config)
        self.setup_logger()

    def setup_logger(self, level: int = logging.ERROR) -> None:
        logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.StreamHandler())
        logger.info("Logger initialized.")

    @staticmethod
    def send_request(url: str, method: str = 'GET', headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None, body: Optional[Dict[str, str]] = None) -> Dict:
        try:
            response = requests.request(method, url, headers=headers or {}, params=params or {}, json=body or {})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Request to {url} failed: {e}")
            return {}

    def clean_text(self, text: str, max_length: int = 512) -> str:
        text = re.sub(r'\s+', ' ', re.sub(r'[^a-zA-Z0-9\s]', '', text))
        return text[:max_length]

    def run_command(self, command: str) -> None:
        subprocess.run(command, shell=True, check=True, capture_output=True)

    def init_models(self, config: Dict) -> Dict:
        set_seed(42)
        models = {}
        for model_config in config.get('model_configs', []):
            name, task = model_config['name'], model_config['task']
            try:
                model = AutoModelForQuestionAnswering.from_pretrained(name)
                tokenizer = AutoTokenizer.from_pretrained(name)
                models[task] = pipeline(task, model=model, tokenizer=tokenizer)
            except Exception as e:
                logging.error(f"Failed to load model {name} for task {task}: {e}")
        return models

    def find_files(self, directory: str) -> List[str]:
        return [os.path.join(root, name) for root, _, names in os.walk(directory) for name in names if not name.startswith('.')]

    @staticmethod
    def load_config(file_path: str) -> Dict:
        with open(file_path) as f:
            return json.load(f)
