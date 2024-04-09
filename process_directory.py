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

    # Example keyword and section extraction
    if 'Python' in file_text:
        keywords.append('Python')
    if 'Introduction' in file_text:
        sections.append('Introduction')
    if 'Code Example' in file_text:
        sections.append('Code Example')

    code_examples = 'Code Example' in sections  # Boolean indicator of code examples

    # Extract content type, audience, and publication date from file path or text
    content_type = 'Tutorial' if 'tutorial' in file_path.lower() else 'Guide'
    audience = 'Developers'  # Default audience, adjust based on your logic
    publication_date = datetime.now().strftime('%Y-%m-%d')  # Current date as publication date

    # Extract document title from Markdown heading or HTML title tag
    soup = BeautifulSoup(file_text, 'html.parser')
    title_tag = soup.find('h1')
    if title_tag:
        title = title_tag.text.strip()

    # Extract tags or categories (customize based on your data source)
    tags = ['python', 'programming']  # Example tags

    # Extract authorship and publication data
    author = 'John Doe'  # Placeholder value, customize extraction based on your data
    affiliation = 'Example Organization'  # Placeholder value, customize extraction
    publication_date = datetime.now().strftime('%Y-%m-%d')  # Current date as publication date

    metadata = {
        'title': title,
        'description': description,
        'keywords': keywords,
        'sections': sections,
        'code_examples': code_examples,
        'content_type': content_type,
        'audience': audience,
        'publication_date': publication_date,
        'document_title': title,
        'file_path': file_path,
        'tags': tags,
        'author': author,
        'affiliation': affiliation,
        'publication_date': publication_date
    }

    return metadata

def extract_contextual_info(file_text, surrounding_sentences=3):
    # Function to extract surrounding text and section headers as contextual information
    surrounding_text = []
    section_headers = []

    paragraphs = file_text.split('\n\n')
    for i, paragraph in enumerate(paragraphs):
        if i <= surrounding_sentences:
            surrounding_text.append(paragraph)
        if i == len(paragraphs) - 1 - surrounding_sentences:
            break

    # Extract section headers (assuming Markdown or HTML format)
    headers = ['# ', '## ', '### ']
    for header in headers:
        for paragraph in paragraphs:
            if paragraph.startswith(header):
                section_header = paragraph[len(header):].strip()
                section_headers.append(section_header)
                break

    context = {
        'surrounding_text': surrounding_text,
        'section_headers': section_headers
    }

    return context

def extract_special_blocks(file_text):
    # Function to extract quotes, citations, and code blocks
    quotes = []
    citations = []
    code_blocks = []

    # Regular expressions to find quotes, citations, and code blocks (adjust as needed)
    quote_pattern = re.compile(r'“([^”]*)”')
    citation_pattern = re.compile(r'\[[^\]]*\]')
    code_block_pattern = re.compile(r'```([^`]*)```', re.MULTILINE)

    for quote_match in quote_pattern.finditer(file_text):
        quotes.append(quote_match.group(1).strip())

    for citation_match in citation_pattern.finditer(file_text):
        citations.append(citation_match.group(0).strip())

    for code_block_match in code_block_pattern.finditer(file_text):
        code_block = code_block_match.group(1).strip()
        code_blocks.append(code_block)

    special_blocks = {
        'quotes': quotes,
        'citations': citations,
        'code_blocks': code_blocks
    }

    return special_blocks

def extract_geographic_context(file_text):
    # Function to extract geographic context from the text
    location_mentions = []  # List of location mentions in the text

    # Regular expression to find location names (customize as needed)
    location_pattern = re.compile(r'\b(city|town|state|country) of (\w+)\b', re.IGNORECASE)

    for location_match in location_pattern.finditer(file_text):
        location = location_match.group(2).strip()
        location_mentions.append(location)

    geographic_context = {
        'location_mentions': location_mentions,
        'target_audience': 'Global'  # Placeholder value, customize extraction
    }

    return geographic_context

def extract_language_and_dialect(file_text):
    # Function to extract language and dialect information
    primary_language = 'English'  # Placeholder value, customize language detection
    dialect = 'American English'  # Placeholder value, customize dialect detection

    language_info = {
        'primary_language': primary_language,
        'dialect': dialect
    }

    return language_info

def extract_intertextual_references(file_text):
    # Function to extract citations and hyperlinks
    citations = []
    hyperlinks = []

    # Regular expressions to find citations and hyperlinks (adjust as needed)
    citation_pattern = re.compile(r'\[[^\]]*\]')
    hyperlink_pattern = re.compile(r'https?://[^\s]+')

    for citation_match in citation_pattern.finditer(file_text):
        citation = citation_match.group(0).strip()
        citations.append(citation)

    for hyperlink_match in hyperlink_pattern.finditer(file_text):
        hyperlink = hyperlink_match.group(0).strip()
        hyperlinks.append(hyperlink)

    intertextual_references = {
        'citations': citations,
        'hyperlinks': hyperlinks
    }

    return intertextual_references

def preprocess_text(text, tokenizer, max_length=512):
    # Function to preprocess text using Hugging Face's Tokenizer
    inputs = tokenizer.encode_plus(
        text, add_special_tokens=True, truncation=True, max_length=max_length, return_tensors='pt'
    )
    tokens = inputs['input_ids'][0].tolist()
    return tokens

def generate_summary(text, summarizer_model, summarizer_tokenizer):
    # Function to generate a summary of the text
    summarizer = pipeline('text-summarization', model=summarizer_model, tokenizer=summarizer_tokenizer)
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return summary

def generate_qa_pairs(tokens, qa_model):
    # Function to generate question-answer pairs using a fine-tuned question-answering model
    qa_pipeline = pipeline('question-answering', model=qa_model, tokenizer=qa_model.tokenizer)
    qa_pairs = qa_pipeline(tokens)
    return qa_pairs

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

def traverse_directories(root_dir):
    # Function to recursively traverse directories and return file paths
    file_paths = []
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            file_path = os.path.join(root, name)
            if file_path.endswith(('.txt', '.md', '.html')):
                file_paths.append(file_path)
    return file_paths

def main():
    # Specify root directory and output file
    root_dir = 'path/to/data_directory'
    output_file = 'structured_data_v0.4.json'

    # Load pre-trained models and tokenizers
    qa_model = AutoModelForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    qa_tokenizer = AutoTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

    summarizer_model = AutoModelForSeq2SeqLM.from_pretrained('t5-base')
    summarizer_tokenizer = AutoTokenizer.from_pretrained('t5-base')

    # Initialize text summarization pipeline
    summarizer = pipeline('text-summarization', model=summarizer_model, tokenizer=summarizer_tokenizer)

    # Traverse directories and process files
    file_paths = traverse_directories(root_dir)
    all_data = []

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            file_text = f.read()
            file_type = file_path.split('.')[-1]  # Get file type from extension

            # Preprocess text using Hugging Face's Tokenizer
            tokens = preprocess_text(file_text, qa_tokenizer)

            # Generate summary for metadata
            summary = generate_summary(file_text, summarizer_model, summarizer_tokenizer)

            # Extract metadata with additional context
            metadata = extract_metadata(file_path, file_text, summary)

            # Extract geographic context
            geographic_context = extract_geographic_context(file_text)

            # Extract language and dialect information
            language_info = extract_language_and_dialect(file_text)

            # Extract inter-textual references (citations and hyperlinks)
            intertextual_refs = extract_intertextual_references(file_text)

            # Extract contextual information
            context = extract_contextual_info(file_text)

            # Extract special text blocks
            special_blocks = extract_special_blocks(file_text)

            # Generate question-answer pairs using fine-tuned QA model
            qa_pairs = generate_qa_pairs(tokens, qa_model)

            # Combine all data into a structured format
            data = {
                'title': metadata['title'],
                'headers': metadata['sections'],
                'paragraph': file_text,
                'surrounding_text': context['surrounding_text'],
                'metadata': metadata,
                'geographic_context': geographic_context,
                'language_info': language_info,
                'intertextual_refs': intertextual_refs,
                'special_blocks': special_blocks,
                'qa_pairs': qa_pairs
            }

            all_data.append(data)

    # Save the structured data to a JSON file
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)

if __name__ == '__main__':
    main()