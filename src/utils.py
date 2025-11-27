def format_duration(seconds):
    """
    Convert seconds into a human-readable format:
    - 0-59 seconds: "X seconds"
    - 1 minute+: "X minutes"
    - 1 hour+: "X hours"
    - 1 day+: "X days"
    """
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hours"
    else:
        days = seconds // 86400
        return f"{days} days"


def sanitize_filename(filename):
    """
    Remove invalid characters from a filename:
    - Remove characters that are not alphanumeric, underscores, or hyphens
    - Trim the filename to a maximum length of 255 characters
    """
    import re
    sanitized = re.sub(r'[^\w\-_]', '_', filename)
    return sanitized[:255]