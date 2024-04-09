import argparse  # Importing the argparse module for command-line parsing
import json  # Importing the json module for JSON data handling
from openai import OpenAI, OpenAIError  # Importing the OpenAI client and error handling
import logging  # Importing the logging module for logging
import time  # Importing the time module for time-related functions
import os  # Importing the os module for operating system functions
import random  # Importing the random module for random number generation
from pathlib import Path  # Importing the Path class from the pathlib module
import nltk  # Importing the nltk module for natural language processing
import tiktoken  # Importing the tiktoken module for tokenization
import markdown  # Importing the markdown module for markdown parsing

# Download necessary NLTK models
nltk.download("punkt")  # Downloading the 'punkt' model for sentence tokenization

# Initialize OpenAI client
client = OpenAI()  # Creating an instance of the OpenAI client
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
)  # Configuring the logging format and level

# Globals
MAX_TOKEN_LIMIT = 1000  # Maximum token limit for OpenAI requests
MAX_CHAR_LIMIT = 4096  # Maximum character limit for OpenAI requests
CONFIG = None  # Will hold the loaded configuration


# 1. load_config() - used in main()
def load_config():
    """
    Loads the configuration from 'finetuning_config.json'.
    Logs a message if the configuration is loaded successfully.
    """
    try:
        logging.info("Loading configuration from 'finetuning_config.json'.")
        with open("finetuning_config.json", "r") as file:
            config = json.load(file)  # Load the configuration from the JSON file
            logging.info("Configuration loaded successfully.")
            return config  # Return the loaded configuration
    except FileNotFoundError as e:
        logging.error(
            "Configuration file not found. Exiting..."
        )  # Log an error if the configuration file is not found
        exit(1)  # Exit the script if the configuration file is not found


# 2. initialize_random_seed() - used in main()
def initialize_random_seed():
    """
    Initializes the random seed if it is present in the configuration.
    """
    if (
        CONFIG and "seed" in CONFIG
    ):  # Check if the 'seed' key is present in the configuration
        random.seed(
            CONFIG["seed"]
        )  # Set the random seed to the value of the 'seed' key in the configuration
        logging.info(
            f"Random seed set to {CONFIG['seed']}."
        )  # Log the random seed value


# 3. chunk_text_nlp() - used in process_file_content()
def chunk_text_nlp(text, max_length=MAX_CHAR_LIMIT):
    """
    Splits the text into chunks using natural language processing to ensure
    semantic integrity. Each chunk has a maximum length of `max_length`.
    Logs each chunk for debugging purposes.
    """
    sentences = nltk.tokenize.sent_tokenize(text)  # Tokenize the text into sentences
    chunks = []  # Initialize an empty list to hold the chunks
    current_chunk = ""  # Initialize an empty string to hold the current chunk
    for sentence in sentences:  # Iterate over each sentence in the text
        if (
            len(current_chunk) + len(sentence) <= max_length
        ):  # Check if adding the current sentence to the current chunk will exceed the maximum length
            current_chunk += (
                sentence + " "
            )  # Add the current sentence to the current chunk
        else:
            chunks.append(
                current_chunk.strip()
            )  # Add the current chunk to the list of chunks
            logging.info(
                f"Chunk added: {current_chunk.strip()[:50]}..."
            )  # Log the first 50 characters of the chunk
            current_chunk = (
                sentence + " "
            )  # Start a new chunk with the current sentence
    if current_chunk:  # Check if there is any remaining text in the current chunk
        chunks.append(
            current_chunk.strip()
        )  # Add the remaining text to the list of chunks
        logging.info(
            f"Final chunk added: {current_chunk.strip()[:50]}..."
        )  # Log the first 50 characters of the final chunk
    return chunks  # Return the list of chunks


# 4. markdown_to_text() - used in process_file_content()
def markdown_to_text(markdown_content):
    """
    Converts markdown content to plain text.
    Placeholder function for markdown parsing.
    """

    markdown_content = markdown.markdown(
        markdown_content
    )  # Parse the markdown content correctly
    logging.info(
        f"Markdown content parsed: {markdown_content[:50]}..."
    )  # Log the first 50 characters of the parsed markdown content

    return markdown_content  # Return the parsed markdown content


# 5. process_file_content() - used in process_files()
def process_file_content(file_content, model, is_markdown=False):
    """
    Handles file content, processing markdown files differently from plain text.
    """
    logging.info(
        "Checking if content is markdown for appropriate processing."
    )  # Log a message indicating that the content is being checked for markdown
    if is_markdown:  # Check if the content is markdown
        logging.info(
            "Converting markdown to text."
        )  # Log a message indicating that the markdown is being converted to text
        file_content = markdown_to_text(
            file_content
        )  # Convert the markdown content to plain text
        logging.info(
            f"Markdown content converted to text: {file_content[:50]}..."
        )  # Log the first 50 characters of the converted markdown content

    estimated_tokens = num_tokens_from_messages(
        [{"role": "user", "content": file_content}], model=model
    )  # Estimate the number of tokens in the file content
    logging.info(f"Estimated tokens: {estimated_tokens}")  # Log the estimated tokens

    if (
        estimated_tokens > MAX_TOKEN_LIMIT
    ):  # Check if the estimated tokens exceed the maximum token limit
        logging.error(
            f"File content exceeds maximum token limit: {estimated_tokens} > {MAX_TOKEN_LIMIT}"
        )  # Log an error if the file content exceeds the maximum token limit
        return None  # Return from the function

    chunks = chunk_text_nlp(file_content)  # Chunk the file content
    logging.info(
        f"File content chunked into {len(chunks)} parts."
    )  # Log the number of chunks

    qa_pairs = generate_qa_pairs(
        chunks, model=model
    )  # Generate Q&A pairs from the chunks
    logging.info(
        f"Q&A pairs generated: {len(qa_pairs)} pairs."
    )  # Log the number of Q&A pairs

    return qa_pairs  # Return the Q&A pairs


# 6. num_tokens_from_messages() - used in process_file_content()
def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    if model == "gpt-3.5-turbo":
        num_tokens = 0
        for message in messages:
            num_tokens += (
                4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            )
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not presently implemented for model {model}."""
        )


def generate_qa_pairs(chunks, model="gpt-3.5-turbo"):
    """
    Generates Q&A pairs from the chunks.
    """
    qa_pairs = []  # Initialize an empty list to hold the Q&A pairs
    for chunk in chunks:  # Iterate over each chunk in the chunks
        try:
            if model.startswith("gpt-3.5"):
                response = client.completions.create(
                    model=model,
                    prompt=chunk,
                    max_tokens=MAX_TOKEN_LIMIT,
                    n=1,
                    stop=None,
                    temperature=0.5,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    best_of=1,
                )  # Generate a Q&A pair from the chunk
            else:
                response = client.create_chat_completion(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Q&A session"},
                        {"role": "user", "content": chunk},
                    ],
                )  # Use chat completions for chat models
            logging.info(
                f"Q&A pair generated: {response.choices[0].text.strip()[:50]}..."
            )  # Log the first 50 characters of the generated Q&A pair
            qa_pairs.append(
                {
                    "question": chunk,
                    "answer": response.choices[0].text.strip(),
                }
            )  # Add the Q&A pair to the list of Q&A pairs
        except OpenAIError as e:
            logging.error(f"OpenAI error: {e}")
            break
        except Exception as e:
            logging.error(f"Error: {e}")
            break
    return qa_pairs  # Return the list of Q&A pairs


def process_directory(input_dir, output_file, model="gpt-3.5-turbo"):
    """
    Processes all files in the input directory and generates Q&A pairs.
    """
    logging.info(f"Processing directory '{input_dir}' for model '{model}'.")
    print(f"Input directory: {input_dir}, Output file: {output_file}, Model: {model}")

    if not os.getenv("OPENAI_API_KEY"):
        logging.error(
            "OPENAI_API_KEY environment variable is not set. Please configure it before running the script."
        )
        return

    input_path = Path(input_dir)
    if "*" in input_dir:
        file_paths = list(input_path.parent.glob(input_path.name))
    else:
        file_paths = list(input_path.rglob("*"))

    print(f"File paths: {file_paths}")

    output_data = []
    for file_path in file_paths:
        if file_path.is_file() and file_path.suffix in [".txt", ".md"]:
            logging.info(
                f"Processing file: {file_path}"
            )  # Log the file path being processed
            with open(file_path, "rb") as f:
                raw_data = f.read(32)  # Read the first 32 bytes to determine encoding
            encoding = "utf-8" if b"\x00" not in raw_data else "utf-16"
            file_content = file_path.read_text(encoding=encoding)
            estimated_tokens = num_tokens_from_messages(
                [{"role": "user", "content": file_content}], model=model
            )
            if estimated_tokens > MAX_TOKEN_LIMIT:
                logging.info("Token count exceeds limit, chunking text for processing.")
                chunks = chunk_text_nlp(file_content, MAX_TOKEN_LIMIT)
                for chunk in chunks:
                    logging.info("Processing chunk with estimated tokens within limit.")
                    qa_pairs = generate_qa_pairs([chunk], model)
                    output_data.extend(qa_pairs)
            else:
                logging.info("Token count within limit, processing file content.")
                qa_pairs = generate_qa_pairs([file_content], model)
                output_data.extend(qa_pairs)

    with open(
        output_file, "a" if os.path.exists(output_file) else "w", encoding="utf-8"
    ) as out_file:
        for item in output_data:
            out_file.write(json.dumps(item) + "\n")

    logging.info(f"Processing complete. Output written to '{output_file}'.")


def main():
    """
    Main function to run the process_directory function.
    """
    try:
        input_dir = CONFIG["input_dir"]
        output_file = CONFIG["output_file"]
        model = CONFIG["model"]
        process_directory(input_dir, output_file, model)
    except KeyError as e:
        logging.error(f"Missing configuration key: {e}")


if __name__ == "__main__":
    CONFIG = load_config()
    initialize_random_seed()
    main()
