import re
import magic
import logging

# Configure logger
logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO)

def detect_malicious_patterns(pdf_path):
    malicious_patterns = [
        r"javascript\s*:",
        r"javascript*",
        r"alert\(",
        r"alert*",
        r"<script>",
        r"document\.cookie",
        r"eval\(",
        r"on\w+\s*=",
        r"location\.href",
        r"window\.open\(",
        r"iframe\s+src=",
        r"img\s+src=",
        r"expression\(",
        r"data:application/javascript,",
        r"data:text/javascript,",
        r"data:image/svg\+xml;base64,",
        r"<svg/onload=",
        r"confirm\(",
        r"prompt\(",
        r"onerror=",
        r"onload=",
        r"<svg/onload=",
        r"new\s+Function\(",
        r"try\s*\{\s*app\.alert\s*\\(\"[^\"]*\"\\)",
        r"app\.openDoc\(\"[^\"]*\"\);",
        r"catch\s*\\(e\\)\s*\{\s*app\.alert\s*\\(e\.message\\);",
        r"try\s*\{\s*app\.alert\s*\\\(\\\"[^\"]*\\\"\\\)",
        r"catch\s*\\\(e\\\)\\s*\{\s*app\.alert\s*\\\(e\.message\\\)\\;",
        r"\\\(\s*app\.alert\\\(\"XSS\"\\\)\s*\\\)",
        # Add more patterns as needed
    ]

    pdf_content = pdf_path.read().decode("latin-1")


    for pattern in malicious_patterns:
        if re.search(pattern, pdf_content, re.IGNORECASE):
            return True

    return False

def detect_malicious_patterns_in_media(file_path):
    # Check the file type using python-magic
    file_type = magic.Magic()
    mime_type = file_type.from_file(file_path)

    malicious_patterns = [
            r"javascript\s*:",
            r"javascript*",
            r"alert\(",
            r"alert*",
            r"<script>",
            r"document\.cookie",
            r"eval\(",
            r"on\w+\s*=",
            r"location\.href",
            r"window\.open\(",
            r"iframe\s+src=",
            r"img\s+src=",
            r"expression\(",
            r"data:application/javascript,",
            r"data:text/javascript,",
            r"data:image/svg\+xml;base64,",
            r"<svg/onload=",
            r"confirm\(",
            r"prompt\(",
            r"onerror=",
            r"onload=",
            r"<svg/onload=",
            r"new\s+Function\(",
            r"try\s*\{\s*app\.alert\s*\\(\"[^\"]*\"\\)",
            r"app\.openDoc\(\"[^\"]*\"\);",
            r"catch\s*\\(e\\)\s*\{\s*app\.alert\s*\\(e\.message\\);",
            r"try\s*\{\s*app\.alert\s*\\\(\\\"[^\"]*\\\"\\\)",
            r"catch\s*\\\(e\\\)\\s*\{\s*app\.alert\s*\\\(e\.message\\\)\\;",
            r"\\\(\s*app\.alert\\\(\"XSS\"\\\)\s*\\\)",
            # Add more patterns as needed
        ]

    # Define malicious patterns based on the file type
    malicious_patterns_file = {
        'image': malicious_patterns,
        'audio': malicious_patterns,
        'video': malicious_patterns,
        'document': malicious_patterns,
    }

    media_type = None
    if 'image' in mime_type:
        media_type = 'image'
    elif 'audio' in mime_type:
        media_type = 'audio'
    elif 'video' in mime_type:
        media_type = 'video'
    elif 'application/pdf' in mime_type:
        media_type = 'document'
    # Add more media types as needed

    # Check for malicious patterns based on the media type
    if media_type and media_type in malicious_patterns:
        with open(file_path, 'rb') as file:
            content = file.read().decode(errors='ignore')  # Read content as text
            for pattern in malicious_patterns_file[media_type]:
                if re.search(pattern, content, re.IGNORECASE):
                    return True

    return False

from collections import OrderedDict

def format_record(record, indent=0):
    """Recursively format an OrderedDict record with proper indentation"""
    output = []
    indent_str = ' ' * indent
    for key, value in record.items():
        if isinstance(value, OrderedDict):
            output.append(f"{indent_str}{key}:")
            output.append(format_record(value, indent + 4))
        elif isinstance(value, list):
            output.append(f"{indent_str}{key}: [")
            for item in value:
                if isinstance(item, OrderedDict):
                    output.append(format_record(item, indent + 8))
                else:
                    output.append(f"{' ' * (indent + 4)}{item}")
            output.append(f"{indent_str}]")
        elif isinstance(value, dict):
            output.append(f"{indent_str}{key}: {{")
            for k, v in value.items():
                output.append(f"{' ' * (indent + 4)}{k}: {v}")
            output.append(f"{indent_str}}}")
        else:
            output.append(f"{indent_str}{key}: {value}")
    return '\n'.join(output)

def print_formatted_records(records):
    """Print a list of records in a formatted way"""
    for i, record in enumerate(records, 1):
        logger.info(f"\n=== Record {i} ===")
        logger.info(format_record(record))
        logger.info("-" * 50)
