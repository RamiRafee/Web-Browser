def handle_file_url(path):
    """
    Handle the file URL scheme by reading the file content.
    
    Args:
        path (str): The file path.
        
    Returns:
        str: The content of the file.
    """
    with open(path.lstrip('/'), "r", encoding="utf8") as f:
        return f.read()
