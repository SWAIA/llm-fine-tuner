import os
import pathlib
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import json
import re
from beautifulsoup4 import BeautifulSoup
import markdown
import pandas as pd
from transformers import pipeline
from datetime import datetime

def extract_metadata(file_path, file_text, summary):
    # Function to extract metadata from the source file and its contents
    title = os.path.basename(file_path)  # Use the filename as the title
    description = summary  # Use the generated summary as the description
    keywords = []  # List of keywords associated with the document
    sections = []  # List of main sections or chapters in the document

    # Example keyword and section extraction (replace with your logic)
    if 'Python' in file_text:
        keywords.append('Python')
    if 'Introduction' in file_text:
        sections.append('Introduction')
    if 'Code Example' in file_text:
        sections.append('Code Examples')

    code_examples = 'Code Examples' in sections  # Boolean indicator of code examples

    # Extract content type, audience, and publication date from file path or text (customize as needed)
    content_type = 'Tutorial' if 'tutorial' in file_path.lower() else 'Guide'
    audience = 'Developers'  # Default audience, adjust based on your logic
    publication_date = datetime.now().strftime('%Y-%m-%d')  # Current date as publication date

    metadata = {
        'title': title,
        'description': description,
        'keywords': keywords,
        'sections': sections,
        'code_examples': code_examples,
        'content_type': content_type,
        'audience': audience,
        'publication_date': publication_date
    }

    return metadata

def traverse_directories(root_dir):
    # Function to recursively traverse directories and return file paths
    file_paths = []
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            file_path = os.path.join(root, name)
            if file_path.endswith(('.txt', '.md', '.html')):
                file_paths.append(file_path)
    return file_paths

def preprocess_text(text, tokenizer, max_length=512):
    # Function to preprocess text using Hugging Face's Tokenizer
    inputs = tokenizer.encode_plus(
        text, add_special_tokens=True, truncation=True, max_length=max_length, return_tensors='pt'
    )
    tokens = inputs['input_ids'][0].tolist()
    return tokens

def generate_qa_pairs(text, qa_model):
    # Function to generate question-answer pairs using a fine-tuned question-answering model
    qa_pipeline = pipeline('question-answering', model=qa_model, tokenizer=qa_model.tokenizer)
    qa_pairs = qa_pipeline(text)
    return qa_pairs

def summarize_text(text, summarizer_model, summarizer_tokenizer):
    # Function to summarize text using a fine-tuned text summarization model
    summarizer = pipeline('text-summarization', model=summarizer_model, tokenizer=summarizer_tokenizer)
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return summary

def format_output(qa_pairs, metadata, output_file):
    # Function to format output to JSON Lines (.jsonl), including metadata
    with open(output_file, 'w') as f:
        for qa_pair in qa_pairs:
            json_object = {
                'question': qa_pair['question'],
                'answer': qa_pair['answer'],
                'metadata': metadata
            }
            json.dump(json_object, f)
            f.write('\n')

def main():
    # Specify root directory and output file
    root_dir = 'path/to/data_directory'
    output_file = 'processed_data_with_metadata.jsonl'

    # Load pre-trained models and tokenizers
    qa_model = AutoModelForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    qa_tokenizer = AutoTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

    summarizer_model = AutoModelForSeq2SeqLM.from_pretrained('t5-base')
    summarizer_tokenizer = AutoTokenizer.from_pretrained('t5-base')

    # Initialize text summarization pipeline
    summarizer = pipeline('text-summarization', model=summarizer_model, tokenizer=summarizer_tokenizer)

    # Traverse directories and process files
    file_paths = traverse_directories(root_dir)
    all_qa_pairs = []

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            file_text = f.read()
            file_type = file_path.split('.')[-1]  # Get file type from extension

            # Preprocess text using Hugging Face's Tokenizer
            tokens = preprocess_text(file_text, qa_tokenizer)

            # Generate summary for metadata
            summary = summarize_text(file_text, summarizer_model, summarizer_tokenizer)

            # Extract metadata based on source file, contents, etc.
            metadata = extract_metadata(file_path, file_text, summary)

            # Generate question-answer pairs using fine-tuned QA model
            qa_pairs = generate_qa_pairs(tokens, qa_model)

            all_qa_pairs.extend(qa_pairs)

    # Format and save output to .jsonl file, including metadata
    format_output(all_qa_pairs, metadata, output_file)

if __name__ == '__main__':
    main()