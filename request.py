import ssl
import socket
import gzip
from urllib.parse import urlparse, urljoin
# Global dictionary to store open connections
open_connections = {}
cache = {}
def make_http_request(host, port, path, scheme,max_redirects=5):
    """
    Make an HTTP/HTTPS request and return the response content.
    
    Args:
        host (str): The host to connect to.
        port (int): The port to connect to.
        path (str): The path to request.
        scheme (str): The URL scheme (http or https).
        
    Returns:
        str: The content of the response.
    """
    global open_connections, cache
    
    # Check cache first
    cache_key = f"{scheme}://{host}{path}"
    if cache_key in cache:
        cached_response = cache[cache_key]
        if cached_response['valid']:
            print(f"Serving from cache: {cache_key}")
            return cached_response['content']
    
    connection_key = (host, port, scheme)
    if connection_key in open_connections:
        s = open_connections[connection_key]
    else:
        s = create_connection(host, port, scheme)
        open_connections[connection_key] = s

    headers = {
        "Host": host,
        "User-Agent": "Creator/1.0",
        "Accept-Encoding": "gzip"  # Enable gzip compression
    }

    request = f"GET {path} HTTP/1.1\r\n"
    for header, value in headers.items():
        request += f"{header}: {value}\r\n"
    request += "\r\n"
    
    s.send(request.encode("utf8"))
    
    # Use binary mode for reading the response
    response = s.makefile("rb")
    statusline = response.readline()

    # Ensure the status line is handled as bytes
    if isinstance(statusline, bytes):
        statusline = statusline.decode('utf-8')
    
    version, status, explanation = statusline.split(" ", 2)
    
    response_headers = {}
    while True:
        line = response.readline()
        if line == b"\r\n": break
        
        header, value = line.split(b":", 1)
        response_headers[header.lower().decode('utf-8')] = value.strip().decode('utf-8')
    if "location" in response_headers and max_redirects > 0:
        redirect_url = response_headers["location"]
        # Handle absolute and relative URLs
        if redirect_url.startswith('http://') or redirect_url.startswith('https://'):
            new_url = redirect_url
        else:
            # Construct the absolute URL using the original host and scheme
            new_url = urljoin(f"{scheme}://{host}", redirect_url)
        
        # Close the current connection
        s.close()
        del open_connections[connection_key]
        
        # Follow the redirect
        return make_http_request(*parse_url(new_url), max_redirects=max_redirects - 1)
    # Handle caching based on Cache-Control
    should_cache = True
    if 'cache-control' in response_headers:
        cache_control = response_headers['cache-control'].lower()
        if 'no-store' in cache_control:
            should_cache = False
        elif 'max-age' in cache_control:
            max_age = int(cache_control.split('max-age=')[1].split(',')[0])
    
    content = b""
    
    if "content-length" in response_headers:
        content_length = int(response_headers["content-length"])
        content = response.read(content_length)
    elif "transfer-encoding" in response_headers and response_headers["transfer-encoding"] == "chunked":
        # Handle chunked transfer encoding
        while True:
            chunk_size_line = response.readline().strip()
            if not chunk_size_line:
                break
            chunk_size = int(chunk_size_line, 16)
            if chunk_size == 0:
                break
            content += response.read(chunk_size)  
    else:
        content = response.read()  # Read the rest of the response
        # Close the connection
        s.close()
        del open_connections[connection_key]
    # Print the first few bytes to check if it's valid gzip data
    # print("Raw content before decompression:", content[:20])  # Check the first 20 bytes
    # Handle gzip compression
    if 'content-encoding' in response_headers and response_headers['content-encoding'] == 'gzip':
        try:
            content = gzip.decompress(content)
        except gzip.BadGzipFile as e:
            print("Received content is not gzipped, skipping decompression. Error:", e)
            # Log the content for further inspection
            with open("response_content.raw", "wb") as f:
                f.write(content)

    # Cache the response if applicable
    if status.startswith('2') and should_cache:  # 200 OK
        cache[cache_key] = {'content': content, 'valid': True}


    return content.decode('utf-8')

def create_connection(host, port, scheme):
    """Create a new connection to the specified host."""
    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP,
    )
    s.connect((host, port))
    if scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)
    return s
def parse_url(url):
    """Parse the URL and return host, port, path, and scheme."""
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    path = parsed.path or '/'
    return host, port, path, parsed.scheme