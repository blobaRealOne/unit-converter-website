import unittest
from io import BytesIO
from typing import override
from unittest.mock import Mock, patch

from src.main import RequestHandler


class TestRequestHandler(unittest.TestCase):
    @override
    def setUp(self):
        self.handler = Mock()  # pyright: ignore[reportUninitializedInstanceVariable, reportUnannotatedClassAttribute]
        self.handler.path = "/"
        self.handler.wfile = BytesIO()

    @patch("src.main.webpage_main_mod_rt")
    def test_get_main_page(self, mock_page):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        mock_page.return_value = b"<html>Test</html>"

        RequestHandler.do_GET(self.handler)

        mock_page.assert_called_once_with("length", False)  # pyright: ignore[reportUnknownMemberType]
        self.handler.send_response.assert_called_once_with(200)  # pyright: ignore[reportAny]

        self.assertIn(b"<html>Test</html>", self.handler.wfile.getvalue())  # pyright: ignore[reportAny]

    def test_get_unknown_path(self):
        self.handler.path = "/unknown"

        RequestHandler.do_GET(self.handler)

        self.handler.send_error.assert_called_once_with(404)  # pyright: ignore[reportAny]


if __name__ == "__main__":
    _ = unittest.main()
