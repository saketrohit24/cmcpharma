"""
Validation utilities for input validation and data integrity
"""
import re
from typing import Any, List, Dict, Optional
from datetime import datetime
from pathlib import Path


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (with or without dots)
        
    Returns:
        True if extension is allowed
    """
    file_ext = Path(filename).suffix.lower()
    normalized_extensions = [
        ext if ext.startswith('.') else f'.{ext}' 
        for ext in allowed_extensions
    ]
    return file_ext in normalized_extensions


def validate_file_size(file_size: int, max_size: int) -> bool:
    """
    Validate file size
    
    Args:
        file_size: Size of file in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if file size is within limits
    """
    return 0 < file_size <= max_size


def validate_document_title(title: str) -> tuple[bool, Optional[str]]:
    """
    Validate document title
    
    Args:
        title: Document title to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not title or not title.strip():
        return False, "Title cannot be empty"
    
    if len(title.strip()) < 3:
        return False, "Title must be at least 3 characters long"
    
    if len(title) > 200:
        return False, "Title cannot exceed 200 characters"
    
    # Check for invalid characters
    invalid_chars = '<>:"/\\|?*'
    if any(char in title for char in invalid_chars):
        return False, f"Title cannot contain these characters: {invalid_chars}"
    
    return True, None


def validate_citation_data(citation_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate citation data
    
    Args:
        citation_data: Citation data to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    if not citation_data.get('text'):
        errors.append("Citation text is required")
    
    if not citation_data.get('source'):
        errors.append("Citation source is required")
    
    page = citation_data.get('page')
    if page is not None:
        if not isinstance(page, int) or page < 1:
            errors.append("Page number must be a positive integer")
    
    # DOI format validation
    doi = citation_data.get('doi')
    if doi:
        doi_pattern = r'^10\.\d+/.+'
        if not re.match(doi_pattern, doi):
            errors.append("Invalid DOI format")
    
    # URL validation
    url = citation_data.get('url')
    if url:
        url_pattern = r'^https?://.+'
        if not re.match(url_pattern, url):
            errors.append("Invalid URL format")
    
    # Date validation
    pub_date = citation_data.get('publication_date')
    if pub_date:
        if isinstance(pub_date, str):
            try:
                datetime.fromisoformat(pub_date)
            except ValueError:
                errors.append("Invalid publication date format")
        elif not isinstance(pub_date, datetime):
            errors.append("Publication date must be a datetime or ISO string")
    
    return len(errors) == 0, errors


def validate_template_data(template_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate template data
    
    Args:
        template_data: Template data to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    if not template_data.get('name'):
        errors.append("Template name is required")
    elif len(template_data['name'].strip()) < 3:
        errors.append("Template name must be at least 3 characters long")
    
    # Type validation
    template_type = template_data.get('type')
    if template_type not in ['uploaded', 'manual']:
        errors.append("Template type must be 'uploaded' or 'manual'")
    
    # TOC validation
    toc = template_data.get('toc', [])
    if not isinstance(toc, list):
        errors.append("TOC must be a list")
    else:
        for i, item in enumerate(toc):
            if not isinstance(item, dict):
                errors.append(f"TOC item {i} must be a dictionary")
                continue
            
            if not item.get('title'):
                errors.append(f"TOC item {i} must have a title")
            
            level = item.get('level')
            if not isinstance(level, int) or level < 1:
                errors.append(f"TOC item {i} level must be a positive integer")
    
    return len(errors) == 0, errors


def validate_generation_request(request_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate generation request data
    
    Args:
        request_data: Generation request data to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    if not request_data.get('template_id'):
        errors.append("Template ID is required")
    
    # Context files validation
    context_files = request_data.get('context_files', [])
    if not isinstance(context_files, list):
        errors.append("Context files must be a list")
    
    # Parameters validation
    parameters = request_data.get('parameters', {})
    if not isinstance(parameters, dict):
        errors.append("Parameters must be a dictionary")
    
    return len(errors) == 0, errors


def validate_export_options(options_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate export options data
    
    Args:
        options_data: Export options to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Format validation
    format_type = options_data.get('format')
    allowed_formats = ['pdf', 'docx', 'html', 'txt']
    if format_type not in allowed_formats:
        errors.append(f"Format must be one of: {', '.join(allowed_formats)}")
    
    # Page size validation
    page_size = options_data.get('page_size')
    if page_size and page_size not in ['a4', 'letter']:
        errors.append("Page size must be 'a4' or 'letter'")
    
    # Margins validation
    margins = options_data.get('margins')
    if margins:
        if not isinstance(margins, dict):
            errors.append("Margins must be a dictionary")
        else:
            required_margin_keys = ['top', 'right', 'bottom', 'left']
            for key in required_margin_keys:
                if key in margins:
                    value = margins[key]
                    if not isinstance(value, (int, float)) or value < 0:
                        errors.append(f"Margin {key} must be a non-negative number")
    
    # Font size validation
    font_size = options_data.get('font_size')
    if font_size and (not isinstance(font_size, int) or font_size < 8 or font_size > 72):
        errors.append("Font size must be between 8 and 72")
    
    return len(errors) == 0, errors


def validate_search_query(query_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate search query data
    
    Args:
        query_data: Search query to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Query text validation
    query_text = query_data.get('query')
    if query_text and len(query_text.strip()) < 2:
        errors.append("Search query must be at least 2 characters long")
    
    # Date range validation
    date_from = query_data.get('date_from')
    date_to = query_data.get('date_to')
    
    if date_from and date_to:
        try:
            if isinstance(date_from, str):
                date_from = datetime.fromisoformat(date_from)
            if isinstance(date_to, str):
                date_to = datetime.fromisoformat(date_to)
            
            if date_from > date_to:
                errors.append("Date 'from' cannot be later than date 'to'")
        except ValueError:
            errors.append("Invalid date format")
    
    # Tags validation
    tags = query_data.get('tags')
    if tags and not isinstance(tags, list):
        errors.append("Tags must be a list")
    
    return len(errors) == 0, errors


def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """
    Sanitize user input
    
    Args:
        input_string: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not input_string:
        return ""
    
    # Remove HTML tags
    input_string = re.sub(r'<[^>]+>', '', input_string)
    
    # Remove script content
    input_string = re.sub(r'<script.*?</script>', '', input_string, flags=re.DOTALL | re.IGNORECASE)
    
    # Limit length
    if len(input_string) > max_length:
        input_string = input_string[:max_length]
    
    # Strip whitespace
    return input_string.strip()


def validate_api_key(api_key: str, service: str) -> tuple[bool, Optional[str]]:
    """
    Validate API key format
    
    Args:
        api_key: API key to validate
        service: Service name (openai, anthropic, etc.)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key or not api_key.strip():
        return False, f"{service} API key cannot be empty"
    
    # Service-specific validation
    if service.lower() == 'openai':
        if not api_key.startswith('sk-'):
            return False, "OpenAI API key must start with 'sk-'"
        if len(api_key) < 20:
            return False, "OpenAI API key appears to be too short"
    
    elif service.lower() == 'anthropic':
        if not api_key.startswith('sk-ant-'):
            return False, "Anthropic API key must start with 'sk-ant-'"
        if len(api_key) < 20:
            return False, "Anthropic API key appears to be too short"
    
    return True, None
