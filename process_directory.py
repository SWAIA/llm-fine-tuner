import argparse
import json
from openai import OpenAI, OpenAIError
import logging
import time
import os
import random
from pathlib import Path
import nltk
import tiktoken
import markdown

nltk.download("punkt")

client = OpenAI()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(funcName)s - %(lineno)d: %(message)s"
)

MAX_TOKEN_LIMIT = 1000
MAX_CHAR_LIMIT = 4096

def load_config():
    try:
        with open("finetuning_config.json", "r") as file:
            config = json.load(file)
            return config
    except FileNotFoundError as e:
        logging.error(
            "Configuration file not found. Exiting..."
        )
        exit(1)

def initialize_random_seed():
    if (
        CONFIG and "seed" in CONFIG
    ):
        random.seed(
            CONFIG["seed"]
        )
        logging.info(
            f"Random seed set to {CONFIG['seed']}."
        )


def chunk_text_nlp(text, max_length=MAX_CHAR_LIMIT):
    sentences = nltk.tokenize.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if (
            len(current_chunk) + len(sentence) <= max_length
        ):
            current_chunk += (
                sentence + " "
            )
        else:
            chunks.append(
                current_chunk.strip()
            )
            logging.info(
                f"Chunk added: {current_chunk.strip()[:50]}..."
            )
            current_chunk = (
                sentence + " "
            )
    if current_chunk:
        chunks.append(
            current_chunk.strip()
        )
        logging.info(
            f"Final chunk added: {current_chunk.strip()[:50]}..."
        )
    return chunks


def markdown_to_text(markdown_content):
    markdown_content = markdown.markdown(
        markdown_content
    )
    logging.info(
        f"Markdown content parsed: {markdown_content[:50]}..."
    )
    return markdown_content


def process_file_content(file_content, model, is_markdown=False):
    if is_markdown:
        file_content = markdown_to_text(
            file_content
        )
    estimated_tokens = num_tokens_from_messages(
        [{"role": "user", "content": file_content}], model=model
    )
    logging.info(f"Estimated tokens: {estimated_tokens}")

    if (
        estimated_tokens > MAX_TOKEN_LIMIT
    ):
        logging.error(
            f"File content exceeds maximum token limit: {estimated_tokens} > {MAX_TOKEN_LIMIT}"
        )
        return None

    chunks = chunk_text_nlp(file_content)
    logging.info(
        f"File content chunked into {len(chunks)} parts."
    )

    qa_pairs = generate_qa_pairs(
        chunks, model=model
    )
    logging.info(
        f"Q&A pairs generated: {len(qa_pairs)} pairs."
    )
    return qa_pairs


def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    if model == "gpt-3.5-turbo":
        num_tokens = 0
        for message in messages:
            num_tokens += (
                4
            )
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += -1
        num_tokens += 2
        return num_tokens
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not presently implemented for model {model}."""
        )

def generate_qa_pairs(chunks, model="gpt-3.5-turbo"):
    """
    Generates Q&A pairs from the chunks.
    """
    qa_pairs = []
    for chunk in chunks:
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Q&A session"},
                    {"role": "user", "content": chunk},
                ],
                model=model,
            )
            logging.info(f"Q&A pair generated: {response.choices[0].message.content[:50]}...")
            qa_pairs.append({"question": chunk, "answer": response.choices[0].message.content})
        except OpenAIError as e:
            logging.error(f"OpenAI error: {e}")
            break
        except Exception as e:
            logging.error(f"Error: {e}")
            break
    return qa_pairs

def process_directory(input_dir, output_file, model="gpt-3.5-turbo"):
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
        if file_path.is_file() and file_path.suffix in [".txt", ".md"] and not file_path.name.startswith("."):
            logging.info(
                f"Processing file: {file_path}"
            )
            with open(file_path, "rb") as f:
                raw_data = f.read(32)
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
