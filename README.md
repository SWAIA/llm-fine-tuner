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
- An active OpenAI API key.
- Required Python packages as listed in `requirements.txt`.

## Installation

1. **Clone the Repository:**

   ```
   git clone https://your-repository-url.git
   cd your-repository-directory
   ```

2. **Install Dependencies:**

   Install the required Python packages using pip:

   ```
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API Key:**

   Set your OpenAI API key as an environment variable. Replace `your_api_key` with your actual OpenAI API key.

   - On Windows:

     ```
     set OPENAI_API_KEY=your_api_key
     ```

   - On Unix/Linux/MacOS:

     ```
     export OPENAI_API_KEY=your_api_key
     ```

## Usage

To run the script, navigate to the project directory in your terminal and execute the following command:

```
python process_directory.py --directory <path_to_directory> [--model <model_name>]
```

- `<path_to_directory>`: The path to the directory containing the text files you want to process.
- `<model_name>`: (Optional) The name of the OpenAI model you wish to use. Defaults to "gpt-3.5-turbo".

Example:

```
python process_directory.py --directory ./texts --model gpt-3.5-turbo
```

This will process all `.txt` files in the `./texts` directory, generating Q&A pairs using the "gpt-3.5-turbo" model, and save the results to `output.jsonl`.

## Output

The script saves the generated Q&A pairs in a JSON Lines file (`output.jsonl`) in the project directory. Each line in the file represents the Q&A generation result for a single input file, including the input file name, generated output, and token usage.

## Contributing

Contributions to the project are welcome. Please follow the standard fork-clone-branch-pull request workflow.

## License

Specify your project's license here.

## Contact

For support or queries, please contact [your email/contact information].
