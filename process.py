import argparse
import os
import json
import fs
from typing import Optional, Dict, Union
from transformers import pipeline
from data_enrichment_main import DataEnrichmentProcessor
from utils import traverse_directories, load_config, save_structured_data, preprocess_text, generate_qa_pairs, get_models_and_pipelines

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
        self.file_paths = traverse_directories(self.input_dir)
        self.data_enrichment_processor = DataEnrichmentProcessor(self.config)
        self.all_data = []

    def _validate_inputs(self, input_dir, output_file, config):
        if not all(isinstance(arg, str) for arg in [input_dir, output_file]) or (config is not None and not isinstance(config, dict)):
            raise ValueError("Invalid input types for DataProcessor initialization")

    def process_files(self):
        for file_path in self.file_paths:
            file_text = fs.readFileSync(file_path, 'utf8')
            preprocessed_text = preprocess_text(file_text)
            qa_pairs = generate_qa_pairs(preprocessed_text)
            models_and_pipelines = get_models_and_pipelines(self.config)
            enriched_data = self.data_enrichment_processor.enrich_data(file_path, preprocessed_text, qa_pairs, models_and_pipelines)
            enriched_data['metadata']['file_path'] = file_path
            self.all_data.append(enriched_data)

        save_structured_data(self.all_data, self.output_file)

# Entry point class for the script
class Main:
    def __init__(self, configuration: Optional[Dict[str, Union[str, Dict]]] = None):
        self._validate_config(configuration)
        self.command_parser = CommandParser()
        self.args = self.command_parser.parse_args()
        self.config = load_config(self.args.config) or configuration
        self.data_processor = DataProcessor(self.args.input_dir, self.args.output_file, self.config)

    def _validate_config(self, configuration):
        if configuration is not None and not isinstance(configuration, dict):
            raise ValueError("Invalid configuration type for Main initialization")

    def run(self):
        self.data_processor.process_files()

# Script entry point
if __name__ == "__main__":
    config = load_config('config.json')  # Default configuration file
    main = Main(config)
    main.run()
