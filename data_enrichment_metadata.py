import os
from datetime import datetime
import re
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from utils import get_models_and_pipelines

class MetadataExtractor:
    def __init__(self, config: Dict):
        # Ensure config is a dictionary
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary.")
        self.config = config
        self.models_and_pipelines = get_models_and_pipelines() or {}

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
