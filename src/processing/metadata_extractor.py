import os
import re
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from datetime import timezone
from typing import Dict, List
from utils import ConfigManager, LoggerService, ModelManager

class ContentHarvester:

    def __init__(self, config: Dict = None):
        self.config_manager = ConfigManager()
        self.config = config if config is not None else asyncio.run(self.config_manager.load_config())
        self.custom_tags = self.config.get('custom_tags', [])
        self.base_url = self.config.get('base_url', 'http://127.0.0.1:8000/')
        self.logger = LoggerService.get_instance("MetadataExtractorLogger")
        self.model_manager = ModelManager(self.logger)
        
    async def extract_metadata(self, file_path: str, file_text: str, summary: str = "") -> Dict:
        soup = BeautifulSoup(file_text, 'html.parser')
        title = await self.extract_title(soup) or os.path.basename(file_path)
        description = summary or await self.extract_description(soup) or ""
        keywords = await self.extract_keywords(soup) or []
        sections = await self.identify_sections(soup) or []
        code_examples = await self.check_for_code_examples(file_text)
        content_type = await self.determine_content_type(file_text) or "unknown"
        publication_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        tags = self.custom_tags
        in_text_references = await self.extract_in_text_references(file_text) or []
        external_links = await self.generate_external_links(keywords) or []

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
        await self.apply_custom_metadata(metadata)
        return metadata
    
    async def extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find('title')
        return title_tag.get_text() if title_tag else None

    async def extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        return [keyword.strip() for keyword in keywords_meta['content'].split(',')] if keywords_meta else []

    async def identify_sections(self, soup: BeautifulSoup) -> List[str]:
        return [header.get_text() for header in soup.find_all(re.compile('^h[1-6]$'))]

    async def extract_in_text_references(self, file_text: str) -> List[str]:
        return [ref.strip() for ref in re.findall(r'\[(.*?)\]', file_text)]

    async def generate_external_links(self, keywords: List[str]) -> List[str]:
        if not self.base_url:
            await self.logger.log("error", "base_url is required in the configuration.")
            raise ValueError("base_url is required in the configuration.")
        return [f"{self.base_url}{keyword.replace(' ', '-').lower()}" for keyword in keywords]

    async def apply_custom_metadata(self, metadata: Dict) -> None:
        custom_metadata = self.config.get('custom_metadata', {})
        metadata.update(custom_metadata)

    async def extract_description(self, soup: BeautifulSoup) -> str:
        description_meta = soup.find('meta', attrs={'name': 'description'})
        return description_meta['content'] if description_meta else ""
    
    async def check_for_code_examples(self, file_text: str) -> List[str]:
        return list(re.findall(r'```(.*?)```', file_text, re.DOTALL))

    async def determine_content_type(self, file_text: str) -> str:
        content_type = "unknown"  # Default to unknown
        try:
            content_type = self.model_manager.determine_content_type(file_text)
        except Exception as e:
            await self.logger.log("error", f"Failed to determine content type: {e}")
        return content_type
