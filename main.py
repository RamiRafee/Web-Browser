import ssl
import socket
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
            with open(self.path, "r", encoding="utf8") as f:
                content = f.read()
            return content
        elif self.scheme == "data":
            _, data = self.data.split(",", 1)
            return data
        else:
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )

            s.connect((self.host, self.port))
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)
            headers = {
                "Host": self.host,
                "Connection": "close",
                "User-Agent": "MyBrowser/1.0"
            }

            request = "GET {} HTTP/1.1\r\n".format(self.path)
            for header, value in headers.items():
                request += "{}: {}\r\n".format(header, value)
            request += "\r\n"

            s.send(request.encode("utf8"))
            response = s.makefile("r", encoding="utf8", newline="\r\n")
            statusline = response.readline()
            version, status, explanation = statusline.split(" ", 2)
            response_headers = {}
            while True:
                line = response.readline()
                if line == "\r\n": break
                header, value = line.split(":", 1)
                response_headers[header.casefold()] = value.strip()
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers
            content = response.read()
            s.close()
            return content
def show(body):
    """
    Display the body content by filtering out HTML tags.
    
    Args:
        body (str): The body content to display.
    """
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")
def load(url):
    """
    Load the content from the given URL and display it.
    
    Args:
        url (URL): The URL object to load content from.
    """
    body = url.request()
    show(body)
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        load(URL(sys.argv[1]))
    else:
        # Default file path for quick testing

        load(URL(""))