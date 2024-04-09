# Large Language Model Data Preparation Utility

## Overview
This project provides a utility for preparing data to fine-tune Large Language Models (LLMs). It includes functionality for recursive directory traversal, text preprocessing, question-answer pair generation, and output formatting. The utility aims to streamline the data preparation process for LLMs, making it efficient and customizable.

## Installation
To install the utility, clone the repository and install the required Python packages:
```bash
git clone https://github.com/your-repository/large-language-model-data-prep.git
cd large-language-model-data-prep
pip install -r requirements.txt
```

## Usage
The utility can be used as a command-line tool or imported as a module in your Python scripts.

### Command-line Usage
To use the utility as a command-line tool, simply run the `process.py` script:
```bash
python process.py --input_dir <input_dir> --output_file <output_file> [--config <config_file>]
```

## Python Module Usage:
You can also import the utility as a module in your Python scripts:
```python
from process import process_files

# Load your configuration
config = load_config('config.json')

# Process files and generate structured data
process_files('input_dir', 'output_file.json', config)
```

The `<input_dir>` argument specifies the path to the directory containing the input files, `<output_file>` is the desired output file path, and `<config_file>` is an optional configuration file.

The example command provided in the README.md, `python process.py --input_dir ./texts --output_file output.jsonl`, would process all `.txt` files in the `./texts` directory, generating Q&A pairs and saving the results to `output.jsonl`.

The Python module usage example, `from process import process_files`, demonstrates how to import the utility as a module and use the `process_files` function to process files and generate structured data.

The commands provided are correct and follow the expected syntax for command-line arguments and Python module usage.
## Configuration
The utility supports configuration through a JSON file. You can customize various aspects of the data preparation process by providing a configuration file. Here's an example configuration:
```json
{
  "max_length": 512,
  "min_length": 30,
  "num_samples": 5,
  "custom_metadata": {
    "additional_field": "value"
  },
  "context_options": {
    "include_coref": true,
    "include_events": true
  },
  "external_data_sources": {
    "api_calls": true
  }
}
```

You can customize the configuration to include additional metadata, control context extraction options, enable/disable external data sources, and more.

## Features
- Recursive directory traversal: Efficiently processes files in nested directories.
- Text preprocessing: Removes markup and non-standard characters, handles HTML and Markdown files.
- Question-answer pair generation: Leverages pre-trained question-answering models for valuable training data.
- Output formatting: Saves structured data in JSON Lines format, compatible with LLM training.
- Customization: Supports configuration options for fine-tuning the data preparation process.
- Efficiency: Handles large datasets efficiently, with optional parallel processing for improved performance.

## License
The Large Language Model Data Preparation Utility is provided under the MIT License.

## Contributing
Contributions to the project are welcome! Please refer to the contribution guidelines in the repository for more information.

## Credits
The Large Language Model Data Preparation Utility is developed and maintained by Your Name or Organization.

# Q&A Generation Script

This project contains a Python script that processes text files within a specified directory to generate question-answer (Q&A) pairs using the OpenAI API. It's designed to facilitate bulk generation of Q&As for applications such as content creation, educational material preparation, and more.

## Features

- **Bulk Processing**: Automatically processes all text files (.txt) within a given directory.
- **OpenAI API Integration**: Utilizes the OpenAI API to generate Q&A pairs from the text content.
- **Efficient Token Handling**: Includes mechanisms to respect token limits for API requests.
- **Custom Model Support**: Allows specifying different models supported by the OpenAI API.
- **Retry Mechanism**: Implements retry logic for handling rate limits and API errors.

## Prerequisites

Before running this script, ensure you have the following prerequisites installed and configured:

- Python 3.8 or newer.
- An active OpenAI API key. Set the `OPENAI_API_KEY` environment variable with your API key.
- Required Python packages as listed in `requirements.txt`.

## Installation and Usage

Please refer to the "Installation" and "Usage" sections above for detailed instructions on installing and using the Large Language Model Data Preparation Utility.

## Output

The script saves the generated Q&A pairs in a JSON Lines file (`output.jsonl`) in the project directory. Each line in the file represents the Q&A generation result for a single input file, including the input file name, generated output, and token usage.

## Contributing

Contributions to the project are welcome. Please refer to the "Contributing" section above for more information.

## License

The Q&A Generation Script is provided under the MIT License.

## Contact

For support or queries regarding the Q&A Generation Script, please contact [your email/contact information].