"""
Helper utilities for common operations
"""
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import json


def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    """
    Generate a unique identifier
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of the random part
        
    Returns:
        Unique identifier string
    """
    random_part = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(length))
    return f"{prefix}{random_part}" if prefix else random_part


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token
    
    Args:
        length: Length of the token
        
    Returns:
        Secure random token
    """
    return secrets.token_urlsafe(length)


def hash_string(input_string: str, algorithm: str = "sha256") -> str:
    """
    Hash a string using specified algorithm
    
    Args:
        input_string: String to hash
        algorithm: Hashing algorithm (sha256, md5, etc.)
        
    Returns:
        Hexadecimal hash string
    """
    hash_func = hashlib.new(algorithm)
    hash_func.update(input_string.encode('utf-8'))
    return hash_func.hexdigest()


def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Calculate hash of a file
    
    Args:
        file_path: Path to the file
        algorithm: Hashing algorithm
        
    Returns:
        Hexadecimal hash of the file
    """
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON with fallback
    
    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: Any = None, **kwargs) -> str:
    """
    Safely serialize object to JSON
    
    Args:
        obj: Object to serialize
        default: Default serializer for non-serializable objects
        **kwargs: Additional arguments for json.dumps
        
    Returns:
        JSON string
    """
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
    
    serializer = default or default_serializer
    
    try:
        return json.dumps(obj, default=serializer, **kwargs)
    except TypeError:
        return json.dumps(str(obj))


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to specified length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def merge_dicts(dict1: Dict, dict2: Dict, deep: bool = True) -> Dict:
    """
    Merge two dictionaries
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        deep: Whether to perform deep merge
        
    Returns:
        Merged dictionary
    """
    if not deep:
        result = dict1.copy()
        result.update(dict2)
        return result
    
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, deep=True)
        else:
            result[key] = value
    
    return result


def flatten_dict(nested_dict: Dict, separator: str = ".") -> Dict:
    """
    Flatten a nested dictionary
    
    Args:
        nested_dict: Dictionary to flatten
        separator: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    def _flatten(obj, parent_key=""):
        items = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                items.extend(_flatten(value, new_key).items())
        else:
            return {parent_key: obj}
        
        return dict(items)
    
    return _flatten(nested_dict)


def get_nested_value(data: Dict, key_path: str, default: Any = None, separator: str = ".") -> Any:
    """
    Get value from nested dictionary using dot notation
    
    Args:
        data: Dictionary to search
        key_path: Dot-separated key path
        default: Default value if key not found
        separator: Key separator
        
    Returns:
        Value at key path or default
    """
    keys = key_path.split(separator)
    current = data
    
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def set_nested_value(data: Dict, key_path: str, value: Any, separator: str = ".") -> Dict:
    """
    Set value in nested dictionary using dot notation
    
    Args:
        data: Dictionary to modify
        key_path: Dot-separated key path
        value: Value to set
        separator: Key separator
        
    Returns:
        Modified dictionary
    """
    keys = key_path.split(separator)
    current = data
    
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return data


def batch_items(items: List[Any], batch_size: int) -> List[List[Any]]:
    """
    Split list into batches
    
    Args:
        items: List to batch
        batch_size: Size of each batch
        
    Returns:
        List of batches
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def retry_on_exception(func, max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Decorator to retry function on exception
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        import time
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt < max_retries:
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise last_exception
        
        return None
    
    return wrapper


def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity using Jaccard index
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Convert to sets of words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard index
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length
        max_keywords: Maximum number of keywords
        
    Returns:
        List of keywords
    """
    import re
    from collections import Counter
    
    # Common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
        'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter words
    keywords = [
        word for word in words 
        if len(word) >= min_length and word not in stop_words
    ]
    
    # Count frequencies and return top keywords
    word_counts = Counter(keywords)
    return [word for word, count in word_counts.most_common(max_keywords)]


def create_timestamp(format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Create formatted timestamp
    
    Args:
        format_string: Timestamp format
        
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format_string)


def parse_timestamp(timestamp_string: str, format_string: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parse timestamp string
    
    Args:
        timestamp_string: Timestamp string to parse
        format_string: Expected format
        
    Returns:
        Parsed datetime or None
    """
    try:
        return datetime.strptime(timestamp_string, format_string)
    except ValueError:
        return None
