import os
import openai
from pathlib import Path
import sys

# Set your OpenAI API key here
openai.api_key = "your_api_key_here"


def chunk_file_content(file_content, chunk_size=1000):
    """Divide file content into manageable chunks."""
    for i in range(0, len(file_content), chunk_size):
        yield file_content[i : i + chunk_size]


def generate_qa_from_chunk(chunk):
    """Use OpenAI's GPT-3.5-turbo to generate a Q&A from a chunk of text."""
    response = openai.Completion.create(
        model="text-davinci-003",  # or "gpt-3.5-turbo" based on your requirement
        prompt=chunk,
        temperature=0.5,
        max_tokens=50,  # Adjust based on the expected length of your Q&A
        n=1,
        stop=None,
    )
    return response.choices[0].text.strip()


def process_directory(directory):
    """Process each file in the directory and its subdirectories."""
    pathlist = Path(directory).rglob("*.*")  # Adjust pattern if needed
    for path in pathlist:
        # because path is object not string
        path_in_str = str(path)
        print(f"Processing file: {path_in_str}")
        try:
            with open(path_in_str, "r", encoding="utf-8") as file:
                content = file.read()
                for chunk in chunk_file_content(content):
                    qa_content = generate_qa_from_chunk(chunk)
                    print(qa_content)
        except Exception as e:
            print(f"An error occurred while processing the file {path_in_str}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a directory path.")
        sys.exit(1)

    directory_path = sys.argv[1]
    if not os.path.isdir(directory_path):
        print("The provided path does not exist or is not a directory.")
        sys.exit(1)

    process_directory(directory_path)
