import os
import re
import json
import logging
import subprocess
import shutil
from bs4 import BeautifulSoup
from transformers import (
    AutoTokenizer, 
    AutoModelForQuestionAnswering, 
    pipeline, 
    set_seed
)
from typing import List, Dict, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Preprocess text for NLP tasks
def preprocess_text(text: str, tokenizer, max_length: int = 512) -> List[int]:
    """Preprocesses text for NLP tasks."""
    if not isinstance(text, str) or not isinstance(max_length, int):
        logging.error("Invalid input types for preprocess_text")
        return []
    try:
        inputs = tokenizer.encode_plus(
            text, add_special_tokens=True, truncation=True, max_length=max_length, return_tensors='pt'
        )
        return inputs['input_ids'][0].tolist()
    except Exception as e:
        logging.error(f"Error in preprocess_text: {e}")
        return []

# Generate question-answer pairs from tokens
def generate_qa_pairs(tokens: List[int], qa_pipeline) -> List[Dict]:
    """Generates question-answer pairs from tokens."""
    if not isinstance(tokens, list) or not all(isinstance(token, int) for token in tokens):
        logging.error("Invalid input types for generate_qa_pairs")
        return []
    try:
        return qa_pipeline(tokens)
    except Exception as e:
        logging.error(f"Error in generate_qa_pairs: {e}")
        return []

# Extract text from file, supports HTML parsing
def extract_text_from_file(file_path: str) -> str:
    """Extracts text from file."""
    if not isinstance(file_path, str):
        logging.error("Invalid input type for extract_text_from_file")
        return ""
    try:
        with open(file_path, 'r') as f:
            file_text = f.read()
        return BeautifulSoup(file_text, 'html.parser').get_text() if file_path.endswith('.html') else file_text
    except Exception as e:
        logging.error(f"Error in extract_text_from_file: {e}")
        return ""

# Save and load structured data to/from a JSON file
def save_structured_data(data: Dict, output_file: str) -> None:
    """Saves data to a JSON file."""
    if not isinstance(data, dict) or not isinstance(output_file, str):
        logging.error("Invalid input types for save_structured_data")
        return
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"Error in save_structured_data: {e}")

def load_config(config_file: str) -> Dict:
    """Loads configuration from a JSON file."""
    if not isinstance(config_file, str):
        logging.error("Invalid input type for load_config")
        return {}
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error in load_config: {e}")
        return {}

# Clean text by removing non-alphanumeric characters
def _clean_text(text: str) -> str:
    """Cleans text."""
    if not isinstance(text, str):
        logging.error("Invalid input type for _clean_text")
        return ""
    try:
        return re.sub(r'[^a-zA-Z0-9\s]', '', text)
    except Exception as e:
        logging.error(f"Error in _clean_text: {e}")
        return ""

# Execute CLI commands with logging
def run_cli_command(command: str) -> None:
    """Executes a CLI command."""
    if not isinstance(command, str):
        logging.error("Invalid input type for run_cli_command")
        return
    try:
        subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(f"Command executed successfully: {command}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command {command}: {e}")
# Logging and Model Management

class LogManager:
    """Manages logging events and log file initialization."""
    def __init__(self, log_file: str = 'data_preparation.log'):
        self.log_file = log_file

    def initialize_log_files(self) -> None:
        """Initializes or resets log files."""
        try:
            with open(self.log_file, 'w') as f:
                f.write("Initializing log files...\n")
            print("Log file initialized.")
        except Exception as e:
            logging.error(f"Error in initialize_log_files: {e}")

    def log_event(self, message: str) -> None:
        """Appends a log event to the log file."""
        try:
# Log events and manage log files
def initialize_log_files(log_file: str = 'data_preparation.log') -> None:
    """Initializes log files."""
    if not isinstance(log_file, str):
        logging.error("Invalid input type for initialize_log_files")
        return
    try:
        with open(log_file, 'w') as f:
            f.write("Initializing log files...\n")
        print("Log file initialized.")
    except Exception as e:
        logging.error(f"Error in initialize_log_files: {e}")

def _log_event(message: str, log_file: str) -> None:
    """Logs events."""
    try:
        with open(log_file, 'a') as f:
            f.write(message + "\n")
        print(message)
    except Exception as e:
        logging.error(f"Error logging event: {e}")

# Load models and pipelines for NLP tasks
def get_models_and_pipelines() -> Optional[Dict[str, Union[AutoModelForQuestionAnswering, AutoTokenizer, pipeline]]]:
    """Loads models and pipelines."""
    try:
        set_seed(42)  # Reproducibility
        models_and_pipelines = {}
        model_configs = [
            ('bert-large-uncased-whole-word-masking-finetuned-squad', 'question-answering'),
            ('t5-base', 'text-summarization'),
            ('bert-base-cased', 'ner'),
            ('distilbert-base-uncased', 'sentiment-analysis'),
            ('bert-base-coref', 'coref-resolution'),
            ('dbmdz/bert-large-cased-event-extraction-llms-2020', 'event-extraction'),
            ('distilbert-base-uncased', 'text-classification'),
            ('bert-base-srl', 'token-classification')
        ]
        for model_name, task in model_configs:
            model = AutoModelForQuestionAnswering.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            pipeline_obj = pipeline(task, model=model, tokenizer=tokenizer)

            # Construct keys for dictionary
            model_key = f"{task}_model"
            tokenizer_key = f"{task}_tokenizer"
            pipeline_key = f"{task}_pipeline"

            # Update dictionary
            models_and_pipelines.update({
                model_key: model,
                tokenizer_key: tokenizer,
                pipeline_key: pipeline_obj
            })

        return models_and_pipelines
    except Exception as e:
        logging.error(f"Error in get_models_and_pipelines: {e}")
        return None
