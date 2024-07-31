import unittest
import gzip
from io import StringIO
from unittest.mock import patch, mock_open, Mock
from main import URL, load, show

from request import make_http_request, open_connections

class TestURL(unittest.TestCase):
    """Tests for the URL class."""
    def test_http_url(self):
        """Test parsing of an HTTP URL."""
        url = URL("http://example.com/path")
        self.assertEqual(url.scheme, "http")
        self.assertEqual(url.host, "example.com")
        self.assertEqual(url.port, 80)
        self.assertEqual(url.path, "/path")

    def test_https_url(self):
        """Test parsing of an HTTPS URL."""
        url = URL("https://example.com/path")
        self.assertEqual(url.scheme, "https")
        self.assertEqual(url.host, "example.com")
        self.assertEqual(url.port, 443)
        self.assertEqual(url.path, "/path")

    def test_file_url(self):
        """Test parsing of a file URL."""
        url = URL("file:///path/to/file")
        self.assertEqual(url.scheme, "file")
        self.assertEqual(url.path, "/path/to/file")
    def test_empty_url(self):
        """Test parsing of an empty URL."""
        url = URL("")
        self.assertEqual(url.scheme, "file")
        self.assertEqual(url.path, "main.py")

    def test_data_url(self):
        """Test parsing of a data URL."""
        url = URL("data:text/html,Hello world!")
        self.assertEqual(url.scheme, "data")
        self.assertEqual(url.data, "text/html,Hello world!")

    def test_view_source_url(self):
        """Test parsing and requesting a view-source URL."""
        url = URL("view-source:http://example.com/path")
        self.assertTrue(url.view_source)
        self.assertEqual(url.scheme, "http")
        self.assertEqual(url.host, "example.com")
        self.assertEqual(url.port, 80)
        self.assertEqual(url.path, "/path")


class TestRequest(unittest.TestCase):
    """Tests for the request method of the URL class."""
    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_file_request(self, mock_file):
        """Test the request method for a file URL."""
        url = URL("file:///path/to/file")
        content = url.request()
        self.assertEqual(content, "file content")

    @patch("socket.socket.connect")
    @patch("socket.socket.send")
    @patch("socket.socket.makefile")
    @patch("ssl.create_default_context")
    def test_http_request(self, mock_ssl_context, mock_makefile, mock_send, mock_connect):
        """Test the request method for an HTTP URL."""
        url = URL("http://example.com/path")
        mock_makefile.return_value.readline.side_effect = [
            b"HTTP/1.1 200 OK\r\n", 
            b"\r\n"
        ]
        mock_makefile.return_value.read.return_value = b"http response content"

        content = url.request()

        self.assertEqual(content, "http response content")

    def test_data_request(self):
        """Test the request method for a data URL."""
        url = URL("data:text/html,Hello world!")
        content = url.request()
        self.assertEqual(content, "Hello world!")

class TestIntegration(unittest.TestCase):
    """Integration tests for the load function."""
    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_load_file_url(self, mock_file):
        """Test loading and displaying content from a file URL."""
        url = URL("file:///path/to/file")
        with patch("sys.stdout", new=StringIO()) as fake_out:
            load(url)
            self.assertEqual(fake_out.getvalue(), "file content")

    def test_load_data_url(self):
        """Test loading and displaying content from a data URL."""
        url = URL("data:text/html,Hello world!")
        with patch("sys.stdout", new=StringIO()) as fake_out:
            load(url)
            self.assertEqual(fake_out.getvalue(), "Hello world!")
    
    def test_load_view_source_url(self):
        """Test loading and displaying content from a view-source URL."""
        
        url = URL("view-source:http://example.com/path")
        with patch("sys.stdout", new=StringIO()) as fake_out:
            load(url)
            output = fake_out.getvalue()
            # Check for the presence of specific elements
            self.assertIn("<!doctype html>", output)
            self.assertIn("<title>Example Domain</title>", output)
            self.assertIn("<h1>Example Domain</h1>", output)
class TestShow(unittest.TestCase):
    """Tests for the show function."""
    def test_show(self):
        """Test show with HTML containing entities."""
        body = "&lt;div&gt;Hello&lt;/div&gt;"
        expected_output = "<div>Hello</div>"
        with patch("sys.stdout", new=StringIO()) as fake_out:
            show(body)
            self.assertEqual(fake_out.getvalue(), expected_output)

    def test_show_with_unknown_entity(self):
        """Test show with an unknown entity."""
        body = "Hello &unknown; world"
        expected_output = "Hello &unknown; world"
        with patch("sys.stdout", new=StringIO()) as fake_out:
            show(body)
            self.assertEqual(fake_out.getvalue(), expected_output)

class TestKeepAlive(unittest.TestCase):
    @patch('socket.socket')
    def test_keep_alive(self, mock_socket):
        
        # Setup mock socket
        mock_conn = Mock()
        mock_socket.return_value = mock_conn
        mock_conn.makefile.return_value.readline.side_effect = [
            b"HTTP/1.1 200 OK\r\n",
            b"Content-Length: 13\r\n",
            b"\r\n"
        ]
        mock_conn.makefile.return_value.read.return_value = b"Hello, World!"

        # First request
        content1 = make_http_request("example.com", 80, "/", "http")



        #self.assertEqual(len(open_connections), 1)

        # Reset mock for second request
        mock_conn.makefile.return_value.readline.side_effect = [
            b"HTTP/1.1 200 OK\r\n",
            b"Content-Length: 11\r\n",
            b"\r\n"
        ]
        mock_conn.makefile.return_value.read.return_value = b"Keep-alive!"

        # Second request
        content2 = make_http_request("example.com", 80, "/test", "http")

        self.assertEqual(len(open_connections), 2)
        print(open_connections)
        # # Verify that socket was created only once
        # mock_socket.assert_called_once()

        # # Verify that send was called twice (once for each request)
        # self.assertEqual(mock_conn.send.call_count, 2)

    @patch('socket.socket')
    def test_different_hosts(self, mock_socket):
        # Setup mock socket
        mock_conn1 = Mock()
        mock_conn2 = Mock()
        mock_socket.side_effect = [mock_conn1, mock_conn2]

        for conn in (mock_conn1, mock_conn2):
            conn.makefile.return_value.readline.side_effect = [
                b"HTTP/1.1 200 OK\r\n",
                b"Content-Length: 13\r\n",
                b"\r\n"
            ]
            conn.makefile.return_value.read.return_value = b"Hello, World!"

        # Request to first host
        content1 = make_http_request("example.com", 80, "/", "http")
        
        self.assertEqual(len(open_connections), 1)

        # Request to second host
        content2 = URL("http://altostrat.com/").request()

        self.assertEqual(len(open_connections), 2)

class TestCaching(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @patch('socket.socket')
    def test_caching(self, mock_socket):
        # Mock the socket responses for the first request
        mock_socket.return_value.makefile.return_value.readline.side_effect = [
            b"HTTP/1.1 200 OK\r\n",
            b"Cache-Control: max-age=3600\r\n",
            b"\r\n",  # End of headers
        ]
        mock_socket.return_value.makefile.return_value.read.return_value = b"Hello, World!"

        # First request should not use cache
        content1 = make_http_request("example.com", 80, "/resource", "http")
        self.assertEqual(content1, "Hello, World!")

        # Mock the socket responses for the second request (should use cache)
        mock_socket.return_value.makefile.return_value.readline.side_effect = [
            b"HTTP/1.1 200 OK\r\n",
            b"Cache-Control: max-age=3600\r\n",
            b"\r\n",  # End of headers
        ]

        # Second request should use cache
        content2 = make_http_request("example.com", 80, "/resource", "http")
        self.assertEqual(content2, b"Hello, World!")

        # Check that the send method was called only once for the first request
        self.assertEqual(mock_socket.return_value.send.call_count, 1)
class TestCompression(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @patch('socket.socket')
    def test_compression(self, mock_socket):
        # Prepare compressed content
        original_content = b"Hello, World!"
        compressed_content = gzip.compress(original_content)

        # Mock the socket responses for a compressed response
        mock_socket.return_value.makefile.return_value.readline.side_effect = [
            b"HTTP/1.1 200 OK\r\n",
            b"Content-Encoding: gzip\r\n",
            b"Content-Length: " + str(len(compressed_content)).encode() + b"\r\n",
            b"\r\n",  # End of headers
        ]
        mock_socket.return_value.makefile.return_value.read.return_value = compressed_content

        # Call the make_http_request function
        content = make_http_request("example.com", 80, "/resource", "http")

        # Assert the decompressed content
        self.assertEqual(content, original_content)
if __name__ == "__main__":
    unittest.main()

