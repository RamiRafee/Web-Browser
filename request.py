import ssl
import socket

def make_http_request(host, port, path, scheme):
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
    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP,
    )

    s.connect((host, port))
    if scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)

    headers = {
        "Host": host,
        "Connection": "close",
        "User-Agent": "MyBrowser/1.0"
    }

    request = "GET {} HTTP/1.1\r\n".format(path)
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