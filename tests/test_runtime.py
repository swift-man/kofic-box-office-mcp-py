import os
import unittest
from unittest.mock import patch

from kofic_box_office_mcp.runtime import DEFAULT_STREAMABLE_HTTP_PATH, RuntimeConfig


class RuntimeTests(unittest.TestCase):
    def test_from_env_uses_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            config = RuntimeConfig.from_env()

        self.assertEqual("127.0.0.1", config.host)
        self.assertEqual(8000, config.port)
        self.assertEqual(DEFAULT_STREAMABLE_HTTP_PATH, config.streamable_http_path)

    def test_from_env_normalizes_path(self):
        with patch.dict(os.environ, {"KOFIC_BOX_OFFICE_MCP_PATH": "custom"}, clear=True):
            config = RuntimeConfig.from_env()

        self.assertEqual("/custom", config.streamable_http_path)


if __name__ == "__main__":
    unittest.main()
