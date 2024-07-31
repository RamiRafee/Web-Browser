import unittest
from io import StringIO
from unittest.mock import patch, mock_open
from main import URL, load, show

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
            "HTTP/1.1 200 OK\r\n", 
            "\r\n"
        ]
        mock_makefile.return_value.read.return_value = "http response content"

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
if __name__ == "__main__":
    unittest.main()
