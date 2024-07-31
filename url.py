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
    def request(self):
        """
        Send a request based on the URL scheme and return the response content.
        
        Returns:
            str: The content of the response.
        """
        if self.scheme == "file":
            return handle_file_url(self.path)
        elif self.scheme == "data":
            return handle_data_url(self.data)
        else:
            return make_http_request(self.host, self.port, self.path, self.scheme)