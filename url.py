import ssl
import socket
from file_handler import handle_file_url
from data_handler import handle_data_url
from request import make_http_request
class URL:
    """A class to parse and handle different types of URLs."""
    def __init__(self, url):
        """
        Initialize the URL object by parsing the input URL string.
        
        Args:
            url (str): The URL string to parse.
        """
        self.url = url
        if url == "about:blank":
            self.scheme = None
            self.host = None
            self.path = None
            self.port = None
            self.is_blank = True
        else:
            self.is_blank = False
            try:
                self.view_source = False
                if url.startswith("view-source:"):
                    self.view_source = True
                    url = url[len("view-source:"):]
                if url.startswith("data:"):
                    # Handle data URLs separately
                    self.scheme = "data"
                    self.data = url[len("data:"):]
                else:
                    # Add file scheme if no scheme is provided
                    if "://" not in url:
                        url = "file://" + url
                    self.scheme, url = url.split("://", 1)
                    assert self.scheme in ["http", "https", "file"]
                    if self.scheme == "http":
                        self.port = 80
                    elif self.scheme == "https":
                        self.port = 443

                    if self.scheme == "file":
                        if url == "":
                            self.path = "main.py"
                        else:
                            self.path =  url
                        self.host = ""
                    else:
                        if "/" not in url:
                            url = url + "/"
                        self.host, url = url.split("/", 1)
                        self.path = "/" + url
                        if ":" in self.host:
                            self.host, port = self.host.split(":", 1)
                            self.port = int(port)
            except ValueError:
                # If URL parsing fails, treat it as about:blank
                self.is_blank = True 
    def request(self):
        """
        Send a request based on the URL scheme and return the response content.
        
        Returns:
            str: The content of the response.
        """
        if self.is_blank:
            return ""  # Return an empty page for about:blank
        content = ""
        if self.scheme == "file":
            content =  handle_file_url(self.path)
        elif self.scheme == "data":
            content =  handle_data_url(self.data)
        else:
            content  = make_http_request(self.host, self.port, self.path, self.scheme)
        if self.view_source:
            return content
        else: 
            return self.render_content(content)

    def render_content(self, content):
        # This method would normally render the HTML content
        # For now, we'll just return the content as is
        return content