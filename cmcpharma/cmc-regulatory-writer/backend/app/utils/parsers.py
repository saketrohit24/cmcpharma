import re
from typing import List
from ..models.template import TOCItem

def parse_toc_from_text(toc_text: str) -> List[TOCItem]:
    """
    Parses a simple text block (e.g., from a textarea) into a list of TOCItem models.
    This is a basic implementation assuming indentation represents hierarchy.
    """
    sections = []
    lines = toc_text.split('\n')

    for line in lines:
        line = line.rstrip() # Keep leading spaces for indentation check
        if not line.strip():
            continue
        
        # Simple level detection based on indentation (e.g., 4 spaces per level)
        leading_spaces = len(line) - len(line.lstrip(' '))
        level = (leading_spaces // 4) + 1

        # Clean up the title by removing numbering and extra spaces
        cleaned_title = re.sub(r'^[\d\w\.\-\s]*[\.\)]\s*', '', line).strip()
        if cleaned_title:
            sections.append(TOCItem(title=cleaned_title, level=level))
            
    return sections
