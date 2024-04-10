import os
from datetime import datetime
import re
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from utils import Utils

class MetadataExtractor:
    def __init__(self, config: Dict):
        # Ensure config is a dictionary
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary.")
        self.config = config
        self.models_and_pipelines = Utils.get_models_and_pipelines() or {}
        self.custom_tags = config.get('custom_tags', [])

    def extract_metadata(self, file_path: str, file_text: str, summary: Optional[str] = None) -> Dict:
        # Validate input types
        if not isinstance(file_path, str) or not isinstance(file_text, str):
            raise ValueError("file_path and file_text must be strings.")
        
        # Extract basic metadata
        title = os.path.basename(file_path)
        description = summary or self.extract_summary(file_text)
        keywords = self.extract_keywords(file_text) or []
        sections = self.identify_sections(file_text) or []
        code_examples = 'Code Example' in sections
        content_type = 'Tutorial' if 'tutorial' in file_path.lower() else 'Guide'
        audience = 'Developers'
        publication_date = datetime.now().strftime('%Y-%m-%d')

        # Enhance metadata with additional details
        title = self.extract_title(file_text) or title
        tags = ['python', 'programming']
        tags.extend(self.custom_tags)
        author = 'John Doe'
        affiliation = 'Example Organization'
        in_text_references = self.extract_in_text_references(file_text) or []
        external_links = self.generate_external_links(keywords) or []
        
        # Compile enriched metadata dictionary
        metadata = {
            'title': title,
            'description': description,
            'keywords': keywords,
            'sections': sections,
            'code_examples': code_examples,
            'content_type': content_type,
            'audience': audience,
            'publication_date': publication_date,
            'document_title': title,  # Duplicate of 'title' for legacy support
            'file_path': file_path,
            'tags': tags,
            'author': author,
            'affiliation': affiliation,
            'in_text_references': in_text_references,
            'external_links': external_links
        }

        # Apply custom configurations to metadata if available
        self.apply_custom_metadata(metadata)
        return metadata

# Tests because it is more convenient to have them in the same file
import unittest
from unittest.mock import patch

class TestMetadataExtraction(unittest.TestCase):
    def setUp(self):
        self.file_path = "test_file.txt"
        self.file_text = "This is a test file."
        self.summary = "Test summary."
        self.expected_metadata = {
            'title': 'test_file.txt',
            'description': 'Test summary.',
            'keywords': [],
            'sections': [],
            'code_examples': False,
            'content_type': 'Guide',
            'audience': 'Developers',
            'publication_date': datetime.now().strftime('%Y-%m-%d'),
            'document_title': 'test_file.txt',
            'file_path': 'test_file.txt',
            'tags': ['python', 'programming'],
            'author': 'John Doe',
            'affiliation': 'Example Organization',
            'in_text_references': [],
            'external_links': []
        }

    @patch('data_enrichment_metadata.extract_summary')
    @patch('data_enrichment_metadata.extract_keywords')
    @patch('data_enrichment_metadata.identify_sections')
    @patch('data_enrichment_metadata.extract_in_text_references')
    @patch('data_enrichment_metadata.generate_external_links')
    def test_extract_metadata(self, mock_generate_external_links, mock_extract_in_text_references, mock_identify_sections, mock_extract_keywords, mock_extract_summary):
        mock_extract_summary.return_value = self.summary
        mock_extract_keywords.return_value = []
        mock_identify_sections.return_value = []
        mock_extract_in_text_references.return_value = []
        mock_generate_external_links.return_value = []

        metadata = self.extract_metadata(self.file_path, self.file_text)
        self.assertEqual(metadata, self.expected_metadata)

if __name__ == '__main__':
    unittest.main()
