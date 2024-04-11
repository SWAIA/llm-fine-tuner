import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List
from ..utils import Utils

class MetadataExtractor:

    def __init__(self, config: Dict = None):
        default_config = Utils.load_config('config.json')
        self.config = config if config is not None else default_config
        self.custom_tags = self.config.get('custom_tags', [])
        self.base_url = self.config.get('base_url', 'http://127.0.0.1:8000/')
        
    def extract_metadata(self, file_path: str, file_text: str, summary: str = "") -> Dict:
        soup = BeautifulSoup(file_text, 'html.parser')
        title = self.extract_title(soup) or os.path.basename(file_path)
        description = summary or self.extract_description(soup) or ""
        keywords = self.extract_keywords(soup) or []
        sections = self.identify_sections(soup) or []
        code_examples = Utils.check_for_code_examples(file_text)
        content_type = Utils.determine_content_type(file_path)
        publication_date = datetime.now().strftime('%Y-%m-%d')
        tags = self.custom_tags
        in_text_references = self.extract_in_text_references(file_text) or []
        external_links = self.generate_external_links(keywords) or []

        metadata = {
            'title': title,
            'description': description,
            'keywords': keywords,
            'sections': sections,
            'code_examples': code_examples,
            'content_type': content_type,
            'publication_date': publication_date,
            'tags': tags,
            'in_text_references': in_text_references,
            'external_links': external_links
        }
        self.apply_custom_metadata(metadata)
        return metadata
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find('title')
        return soup.find('title').get_text() if soup.find('title') else None

    def extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        return [keyword.strip() for keyword in soup.find('meta', attrs={'name': 'keywords'})['content'].split(',')] if soup.find('meta', attrs={'name': 'keywords'}) else []

    def identify_sections(self, soup: BeautifulSoup) -> List[str]:
        return [header.get_text() for header in soup.find_all(re.compile('^h[1-6]$'))]

    def extract_in_text_references(self, file_text: str) -> List[str]:
        return [ref.strip() for ref in re.findall(r'\[(.*?)\]', file_text)]

    def generate_external_links(self, keywords: List[str]) -> List[str]:
        if not self.base_url:
            Utils.log_error("base_url is required in the configuration.")
            raise ValueError("base_url is required in the configuration.")
        return [f"{self.base_url}{keyword.replace(' ', '-').lower()}" for keyword in keywords]

    def apply_custom_metadata(self, metadata: Dict) -> None:
        custom_metadata = self.config.get('custom_metadata', {})
        metadata.update(custom_metadata)
