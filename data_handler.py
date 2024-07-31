def handle_data_url(data):
    """
    Handle the data URL scheme by returning the inlined data.
    
    Args:
        data (str): The data part of the data URL.
        
    Returns:
        str: The inlined data.
    """
    _, data = data.split(",", 1)
    return data
