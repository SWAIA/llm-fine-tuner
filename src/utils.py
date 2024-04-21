from typing import List, Dict
import os
import re
import json
import subprocess
import aiofiles
import aiohttp
import logging
import asyncio
class LoggerService:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, name: str, alert_range: tuple[int, int] = (30, 40)):
        if cls._instance is None:
            cls._instance = super(LoggerService, cls).__new__(cls)
            cls._instance._setup(name, alert_range)
        return cls._instance

    @classmethod
    async def get_instance(cls, name: str, alert_range: tuple[int, int] = (30, 40)):
        if cls._instance is None:
            cls._instance = cls(name, alert_range)
        return cls._instance

    def _setup(self, name: str, alert_range: tuple[int, int] = (30, 40)):
        import sys
        sys.path.append('src/processing')
        from processing.context_extractor import analyze_sentiment

        self.logger = self._initialize_logger(name, alert_range)
        self.lock = self._lock
        self.sentiment_analyzer = analyze_sentiment()
        self.mood_color_mapper = MoodColorMapper()
        self.alert_range = alert_range
        self.subscribers = []

    async def log(self, level: str, message: str, *_args, **_kwargs) -> None:
        sentiment_level = await self.sentiment_analyzer.analyze_sentiment(message)
        adjusted_level = self._adjust_log_level(level, sentiment_level)
        async with self.lock:
            log_method = getattr(self.logger, adjusted_level)
            log_message = f"{message}"
            log_method(log_message, *_args, **_kwargs)
            await self._publish_to_subscribers(log_message)
    def _adjust_log_level(self, original_level: str, sentiment_level: str) -> str:
        if original_level.isdigit():
            original_level_num = int(original_level)
        else:
            original_level_num = logging.getLevelName(original_level.upper())
            if isinstance(original_level_num, str):
                original_level_num = logging.ERROR
        if sentiment_level == 'negative' and not (self.alert_range[0] <= original_level_num <= self.alert_range[1]):
            return 'error'
        return original_level

    def _initialize_logger(self, name: str, alert_range: tuple[int, int] = (30, 40)) -> logging.Logger:
        logging.basicConfig(level=alert_range[0], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        return logging.getLogger(name)

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    async def _publish_to_subscribers(self, message):
        for subscriber in self.subscribers:
            await subscriber.receive(message)


class MoodColorMapper:
    def __init__(self, mood: str = 'neutral'):
        self.mood_categories = {
            'calm': {'hue_range': (180, 240), 'saturation': 0.3},
            'energetic': {'hue_range': (0, 60), 'saturation': 0.8},
            'romantic': {'hue_range': (300, 360), 'saturation': 0.5},
            'vibrant': {'hue_range': (0, 360), 'saturation': 0.9},
            'neutral': {'hue_range': (0, 360), 'saturation': 0.5}
        }
        self.default_mood = mood

    def map_mood_to_color(self, min_hue: float, max_hue: float, mood: str = None) -> str:
        mood = mood or self.default_mood
        for category, values in self.mood_categories.items():
            hue_range = values['hue_range']
            if hue_range[0] <= min_hue * 360 <= hue_range[1] or hue_range[0] <= max_hue * 360 <= hue_range[1]:
                mood = category
                break
        saturation = self.mood_categories[mood]['saturation'] * 100
        hue = (min_hue + max_hue) / 2 * 360
        return f"hsl({hue}, {saturation}%, 50%)"
class ConfigManager:
    def __init__(self, config_path: str = './../config.json') -> None:
        self.config_path = config_path
        self.config = {}

    async def load_config(self) -> Dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file {self.config_path} not found.")
        try:
            async with aiofiles.open(self.config_path, mode='r') as f:
                config_content = await f.read()
                self.config = json.loads(config_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.config_path}.") from e
        return self.config
class RequestManager:
    def __init__(self, logger: LoggerService) -> None:
        self.logger = logger

    async def send_request(self, url: str, method: str = 'GET', headers: Dict[str, str] = None, params: Dict[str, str] = None, body: Dict[str, str] = None) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers or {}, params=params or {}, json=body or {}) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            await self.logger.log("error", f"Request to {url} failed: {e}")
            return {}

class TextProcessor:
    @staticmethod
    def clean_text(text: str, max_length: int = 512) -> str:
        text = re.sub(r'\s+', ' ', re.sub(r'[^a-zA-Z0-9\s]', '', text))
        return text[:max_length]

class ModelManager:
    def __init__(self, logger: LoggerService) -> None:
        self.logger = logger
        self.models = {}

    def init_models(self, config: Dict) -> None:
        from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline, set_seed
        set_seed(42)
        for model_config in config.get('model_configs', []):
            name, task = model_config['name'], model_config['task']
            try:
                model = AutoModelForQuestionAnswering.from_pretrained(name)
                tokenizer = AutoTokenizer.from_pretrained(name)
                self.models[task] = pipeline(task, model=model, tokenizer=tokenizer)
            except Exception as e:
                asyncio.run(self.logger.log("error", f"Failed to load model {name} for task {task}: {e}"))

class FileManager:
    @staticmethod
    def find_files(directory: str) -> List[str]:
        return [os.path.join(root, name) for root, _, names in os.walk(directory) for name in names if not name.startswith('.')]

class ShellMapper:
    def execute_shell_command(self, command: str, parameters: dict, mood: str = 'neutral', sentiment: str = 'neutral') -> None:
        command_with_params = f"{command} {' '.join([str(value) for value in parameters.values()])}"
        mood, sentiment = self._determine_mood_and_sentiment(parameters, mood, sentiment)
        styled_command = self._apply_style_to_command(command_with_params, mood, sentiment)
        try:
            subprocess.run(styled_command, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            asyncio.run(self.logger.log("error", f"Shell command execution failed with mood {mood} and sentiment {sentiment}: {e}"))

    def _determine_mood_and_sentiment(self, parameters: dict, mood: str = 'neutral', sentiment: str = 'neutral') -> tuple:
        if 'urgent' in parameters.values():
            mood = "aggressive"
            sentiment = "negative"
        elif 'routine' in parameters.values():
            mood = "calm"
            sentiment = "positive"
        return mood, sentiment

    def _apply_style_to_command(self, command: str, mood: str, sentiment: str) -> str:
        if mood == "aggressive":
            return f"\033[1;31m{command}\033[0m"
        elif mood == "calm":
            return f"\033[1;34m{command}\033[0m"
        return command
