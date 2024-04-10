import argparse
import os
import json
import logging
from typing import Optional, Dict, Union
from transformers import pipeline
from data_enrichment_main import DataEnrichmentProcessor
from utils import Utils
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Setup for command-line argument parsing
class CommandParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Process files for data preparation')
        self.parser.add_argument('--input_dir', type=str, required=True, help='Input directory containing files to process')
        self.parser.add_argument('--output_file', type=str, required=True, help='Output file path for structured data')
        self.parser.add_argument('--config', type=str, help='Path to configuration file')

    def parse_args(self) -> argparse.Namespace:
        return self.parser.parse_args()

# Main class for processing data files
class DataProcessor:
    def __init__(self, input_dir: str, output_file: str, config: Optional[Dict[str, Union[str, Dict]]]):
        self._validate_inputs(input_dir, output_file, config)
        self.input_dir = input_dir
        self.output_file = output_file
        self.config = config
        self.file_paths = Utils.traverse_directories(self.input_dir)
        self.data_enrichment_processor = DataEnrichmentProcessor(self.config)
        self.all_data = []

    def _validate_inputs(self, input_dir, output_file, config):
        if not all(isinstance(arg, str) for arg in [input_dir, output_file]) or (config is not None and not isinstance(config, dict)):
            logging.error("Invalid input types for DataProcessor initialization")
            raise ValueError("Invalid input types for DataProcessor initialization")

    def process_files(self):
        logging.info("Starting file processing")
        start_time = time.time()
        models_and_pipelines = Utils.get_models_and_pipelines(self.config)
        for file_path in self.file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_text = file.read()
                preprocessed_text = Utils.preprocess_text(file_text, models_and_pipelines['question-answering_tokenizer'])
                qa_pairs = Utils.generate_qa_pairs(preprocessed_text, models_and_pipelines['question-answering_pipeline'])
                enriched_data = self.data_enrichment_processor.enrich_data(file_path, preprocessed_text, qa_pairs, models_and_pipelines)
                enriched_data['metadata']['file_path'] = file_path
                self.all_data.append(enriched_data)
            except Exception as e:
                logging.error(f"Error processing file {file_path}: {e}")

        Utils.save_structured_data(self.all_data, self.output_file)
        end_time = time.time()
        logging.info(f"Processing completed in {end_time - start_time} seconds")

# Entry point class for the script
class Main:
    def __init__(self, configuration: Optional[Dict[str, Union[str, Dict]]] = None):
        self._validate_config(configuration)
        self.command_parser = CommandParser()
        self.args = self.command_parser.parse_args()
        self.config = Utils.load_config(self.args.config) or configuration
        self.data_processor = DataProcessor(self.args.input_dir, self.args.output_file, self.config)

    def _validate_config(self, configuration):
        if configuration is not None and not isinstance(configuration, dict):
            logging.error("Invalid configuration type for Main initialization")
            raise ValueError("Invalid configuration type for Main initialization")

    def run(self):
        logging.info("Starting main run method")
        self.data_processor.process_files()

# Script entry point
if __name__ == "__main__":
    logging.info("Script started")
    config = Utils.load_config('config.json')  # Default configuration file
    main = Main(config)
    main.run()

# Tests because it is more convenient to have them in the same file
import unittest

class TestUtilsMethods(unittest.TestCase):
    def setUp(self):
        self.text = "This is a sample text for testing."
        self.file_path_html = "sample.html"
        self.file_path_txt = "sample.txt"
        self.config_file = "config.json"
        self.invalid_text = 12345  # Not a string
        self.invalid_file_path = 67890  # Not a string
        self.invalid_config_file = 12345  # Not a string

    def test_preprocess_text_valid_input(self):
        tokenizer = Utils.get_models_and_pipelines()['question-answering_tokenizer']
        processed_text = Utils.preprocess_text(self.text, tokenizer)
        self.assertIsInstance(processed_text, list)
        self.assertTrue(len(processed_text) > 0)

    def test_preprocess_text_invalid_input(self):
        tokenizer = Utils.get_models_and_pipelines()['question-answering_tokenizer']
        processed_text = Utils.preprocess_text(self.invalid_text, tokenizer)
        self.assertEqual(processed_text, [])

    def test_extract_text_from_file_html(self):
        extracted_text = Utils.extract_text_from_file(self.file_path_html)
        self.assertIsInstance(extracted_text, str)
        self.assertTrue(len(extracted_text) > 0)

    def test_extract_text_from_file_txt(self):
        extracted_text = Utils.extract_text_from_file(self.file_path_txt)
        self.assertIsInstance(extracted_text, str)
        self.assertTrue(len(extracted_text) > 0)

