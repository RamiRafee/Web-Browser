import sys
from url import URL
from utils import show

def load(url):
    """
    Load the content from the given URL and display it.
    
    Args:
        url (URL): The URL object to load content from.
    """
    body = url.request()
    if url.view_source:
        print(body)  # Print the raw HTML source
    else:
        show(body)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        load(URL(sys.argv[1]))
    else:
        # Default file path for quick testing

        load(URL(""))
