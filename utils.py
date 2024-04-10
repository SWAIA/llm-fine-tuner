import os
import re
import json
import logging
import subprocess
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

class Utils:
    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def clean_text(text: str) -> str:
        """Cleans text by removing non-alphanumeric characters."""
        if not isinstance(text, str):
            logging.error("Invalid input type for clean_text")
            return ""
        try:
            return re.sub(r'[^a-zA-Z0-9\s]', '', text)
        except Exception as e:
            logging.error(f"Error in clean_text: {e}")
            return ""

    @staticmethod
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

    @staticmethod
    def get_models_and_pipelines() -> Optional[Dict[str, Union[AutoModelForQuestionAnswering, AutoTokenizer, pipeline]]]:
        """Loads models and pipelines."""
        try:
            ('gpt-3', 'text-generation'),
        ]
        for model_name, task in model_configs:
            try:
                model = AutoModelForQuestionAnswering.from_pretrained(model_name)
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                if task == 'question-answering':
                    qa_pipeline = pipeline(task, model=model, tokenizer=tokenizer)
                    models_and_pipelines[model_name] = {'model': model, 'tokenizer': tokenizer, 'pipeline': qa_pipeline}
                else:
                    models_and_pipelines[model_name] = {'model': model, 'tokenizer': tokenizer}
            except Exception as e:
                logging.error(f"Error loading model {model_name} for task {task}: {e}")
            set_seed(42)  # Reproducibility
    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def _clean_text(text: str) -> str:
        """Cleans text by removing non-alphanumeric characters."""
        if not isinstance(text, str):
            logging.error("Invalid input type for _clean_text")
            return ""
        try:
            return re.sub(r'[^a-zA-Z0-9\s]', '', text)
        except Exception as e:
            logging.error(f"Error in _clean_text: {e}")
            return ""

    @staticmethod
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

class Utils:
    """Utility class for common functions."""
    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def test_preprocess_text():
        """Test the preprocess_text function."""
        test_text = "This is a test text."
        test_max_length = 20
        # Initialize tokenizer
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        # Call the function with test parameters
        tokens = Utils.preprocess_text(test_text, tokenizer, test_max_length)
        # Verify the output is a list of integers
        assert isinstance(tokens, list) and all(isinstance(token, int) for token in tokens), "The preprocess_text function failed to return a list of integers."
        print("test_preprocess_text passed.")

    @staticmethod
    def test_generate_qa_pairs():
        """Test the generate_qa_pairs function."""
        test_tokens = [101, 2023, 2003, 1037, 3231, 3793, 1012, 102]
        # Initialize QA pipeline
        qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
        # Call the function with test parameters
        qa_pairs = Utils.generate_qa_pairs(test_tokens, qa_pipeline)
        # Verify the output is a list of dictionaries
        assert isinstance(qa_pairs, list) and all(isinstance(pair, dict) for pair in qa_pairs), "The generate_qa_pairs function failed to return a list of dictionaries."
        print("test_generate_qa_pairs passed.")

    @staticmethod
    def test_extract_text_from_file():
        """Test the extract_text_from_file function."""
        test_file_path = "test_file.txt"
        # Create a test file
        with open(test_file_path, 'w') as f:
            f.write("This is a test file.")
        # Call the function with test parameters
        extracted_text = Utils.extract_text_from_file(test_file_path)
        # Verify the output is a string containing the file content
        assert isinstance(extracted_text, str) and extracted_text == "This is a test file.", "The extract_text_from_file function failed to extract the correct text."
        # Cleanup
        os.remove(test_file_path)
        print("test_extract_text_from_file passed.")

    @staticmethod
    def test_save_and_load_structured_data():
        """Test the save_structured_data and load_config functions together."""
        test_data = {"key": "value"}
        test_output_file = "test_data.json"
        # Call the save function with test parameters
        Utils.save_structured_data(test_data, test_output_file)
        # Call the load function to retrieve the data
        loaded_data = Utils.load_config(test_output_file)
        # Verify the loaded data matches the original data
        assert loaded_data == test_data, "The save_structured_data or load_config function failed to correctly save and load the data."
        # Cleanup
        os.remove(test_output_file)
        print("test_save_and_load_structured_data passed.")

    @staticmethod
    def test_run_cli_command():
        """Test the run_cli_command function."""
        test_command = "echo Test command"
        # Call the function with test parameters
        Utils.run_cli_command(test_command)
        # Verify the command was executed successfully
