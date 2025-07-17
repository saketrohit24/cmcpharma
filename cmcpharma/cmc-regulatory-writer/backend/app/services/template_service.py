from typing import List, Optional, Dict
from ..models.template import Template, TemplateCreationRequest, TOCItem
from ..utils.parsers import parse_toc_from_text
import uuid
import os
from pathlib import Path

# Add document processing imports
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
import re

class TemplateService:
    def __init__(self):
        # In-memory storage for templates (replace with database in production)
        self.templates_storage: Dict[str, Template] = {}
        self._initialize_sample_templates()
    
    def _initialize_sample_templates(self):
        """Initialize with some sample templates"""
        sample_template = Template(
            id="sample-1",
            name="Module 3.2.S Drug Substance",
            description="Complete template for drug substance documentation",
            toc=[
                TOCItem(id="1", title="General Information", level=1),
                TOCItem(id="2", title="Nomenclature", level=2),
                TOCItem(id="3", title="Structure", level=2),
                TOCItem(id="4", title="General Properties", level=2),
                TOCItem(id="5", title="Manufacture", level=1),
                TOCItem(id="6", title="Manufacturer(s)", level=2),
                TOCItem(id="7", title="Description of Manufacturing Process", level=2),
                TOCItem(id="8", title="Control of Materials", level=2),
                TOCItem(id="9", title="Characterisation", level=1),
                TOCItem(id="10", title="Control of Drug Substance", level=1),
            ]
        )
        self.templates_storage[sample_template.id] = sample_template
    
    def create_template_from_text(self, request: TemplateCreationRequest) -> Template:
        """
        Creates a structured Template object from a raw text request.
        """
        parsed_toc = parse_toc_from_text(request.toc_text)
        
        new_template = Template(
            name=request.name,
            description=request.description,
            toc=parsed_toc
        )
        
        # Save the template
        self.templates_storage[new_template.id] = new_template
        return new_template
    
    async def get_all_templates(self) -> List[Template]:
        """Get all saved templates"""
        return list(self.templates_storage.values())
    
    async def get_template_by_id(self, template_id: str) -> Optional[Template]:
        """Get a specific template by ID"""
        return self.templates_storage.get(template_id)
    
    async def save_template(self, template: Template) -> Template:
        """Save a template"""
        self.templates_storage[template.id] = template
        return template
    
    async def update_template(self, template_id: str, template_data: dict) -> Optional[Template]:
        """Update an existing template"""
        if template_id in self.templates_storage:
            template = self.templates_storage[template_id]
            if 'name' in template_data:
                template.name = template_data['name']
            if 'description' in template_data:
                template.description = template_data['description']
            if 'toc' in template_data:
                template.toc = template_data['toc']
            return template
        return None
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        if template_id in self.templates_storage:
            del self.templates_storage[template_id]
            return True
        return False
    
    async def create_template_from_uploaded_file(self, file_path: str, template_name: str = None, description: str = "") -> Template:
        """
        Create a template from an uploaded file (PDF, TXT, DOCX)
        Extracts structure and content from the file
        """
        try:
            # Extract content from file
            content = await self._extract_content_from_file(file_path)
            
            # Parse structure from content
            toc_items = await self._extract_structure_from_content(content)
            
            # Generate template name if not provided
            if not template_name:
                template_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Create template
            new_template = Template(
                name=template_name,
                description=description or f"Template created from uploaded file: {os.path.basename(file_path)}",
                toc=toc_items
            )
            
            # Store additional metadata
            new_template.source_file = os.path.basename(file_path)
            new_template.content = content
            new_template.type = "uploaded"
            
            # Save the template
            self.templates_storage[new_template.id] = new_template
            return new_template
            
        except Exception as e:
            raise Exception(f"Failed to create template from file {file_path}: {str(e)}")
    
    async def _extract_content_from_file(self, file_path: str) -> str:
        """Extract text content from various file types"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension in ['.txt', '.md']:
                loader = TextLoader(file_path, encoding='utf-8')
            elif file_extension in ['.doc', '.docx']:
                loader = UnstructuredWordDocumentLoader(file_path)
            else:
                # Fallback to text loader
                loader = TextLoader(file_path, encoding='utf-8')
            
            documents = loader.load()
            content = "\n\n".join([doc.page_content for doc in documents])
            return content
            
        except Exception as e:
            raise Exception(f"Failed to extract content from {file_path}: {str(e)}")
    
    async def _extract_structure_from_content(self, content: str) -> List[TOCItem]:
        """
        Extract hierarchical structure from document content
        Looks for headings, numbered sections, etc.
        """
        toc_items = []
        lines = content.split('\n')
        
        # Patterns to match different heading styles
        patterns = [
            # Numbered patterns like "1.", "1.1", "1.1.1"
            (r'^(\d+(?:\.\d+)*)\.\s+(.+)$', lambda m: (len(m.group(1).split('.')), m.group(2).strip())),
            # Markdown headers like "# Title", "## Subtitle"
            (r'^(#{1,6})\s+(.+)$', lambda m: (len(m.group(1)), m.group(2).strip())),
            # ALL CAPS headings
            (r'^([A-Z][A-Z\s]{3,})$', lambda m: (1, m.group(1).strip())),
            # Underlined headings (next line has === or ---)
            (r'^(.+)$', lambda m: (1, m.group(1).strip()) if len(m.group(1)) > 3 else None),
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check each pattern
            for pattern, level_extractor in patterns:
                match = re.match(pattern, line)
                if match:
                    result = level_extractor(match)
                    if result:
                        level, title = result
                        
                        # For underlined headings, check next line
                        if pattern == r'^(.+)$' and i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if re.match(r'^[=-]{3,}$', next_line):
                                # This is an underlined heading
                                pass
                            else:
                                continue
                        
                        # Skip very short titles or common words
                        if len(title) < 3 or title.lower() in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']:
                            continue
                        
                        # Ensure reasonable level (1-4)
                        level = min(max(level, 1), 4)
                        
                        toc_items.append(TOCItem(
                            title=title,
                            level=level
                        ))
                        break
        
        # If no structure found, create basic sections
        if not toc_items:
            toc_items = self._create_default_structure_from_content(content)
        
        return toc_items
    
    def _create_default_structure_from_content(self, content: str) -> List[TOCItem]:
        """Create a default structure when no clear hierarchy is found"""
        # Look for key pharmaceutical sections in content
        pharma_sections = [
            ("Introduction", ["introduction", "overview", "summary"]),
            ("General Information", ["general", "description", "product"]),
            ("Manufacturing", ["manufacturing", "process", "production"]),
            ("Quality Control", ["quality", "control", "testing", "specification"]),
            ("Analytical Methods", ["analytical", "method", "analysis", "hplc"]),
            ("Stability", ["stability", "storage", "shelf"]),
            ("Regulatory", ["regulatory", "compliance", "ich", "guideline"]),
            ("Conclusion", ["conclusion", "summary", "result"])
        ]
        
        found_sections = []
        content_lower = content.lower()
        
        for section_name, keywords in pharma_sections:
            if any(keyword in content_lower for keyword in keywords):
                found_sections.append(TOCItem(title=section_name, level=1))
        
        # If still no sections, create generic ones
        if not found_sections:
            found_sections = [
                TOCItem(title="Introduction", level=1),
                TOCItem(title="Main Content", level=1),
                TOCItem(title="Conclusion", level=1)
            ]
        
        return found_sections
