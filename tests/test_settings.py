import os
import unittest
from unittest.mock import patch

from kofic_box_office_mcp.exceptions import ArkoEventError, KoficBoxOfficeError, McstPerformanceError
from kofic_box_office_mcp.settings import ArkoEventSettings, KoficBoxOfficeSettings, McstPerformanceSettings


class SettingsTests(unittest.TestCase):
    def test_kofic_settings_require_kofic_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(KoficBoxOfficeError):
                KoficBoxOfficeSettings.from_env()

    def test_arko_settings_require_arko_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ArkoEventError):
                ArkoEventSettings.from_env()

    def test_kofic_settings_read_only_kofic_key(self):
        with patch.dict(
            os.environ,
            {
                "KOFIC_BOX_OFFICE_SERVICE_KEY": "kofic-secret",
                "ARKO_EVENT_SERVICE_KEY": "arko-secret",
                "MCST_PERFORMANCE_SERVICE_KEY": "mcst-secret",
            },
            clear=True,
        ):
            settings = KoficBoxOfficeSettings.from_env()

        self.assertEqual("kofic-secret", settings.service_key.raw_key)

    def test_arko_settings_read_only_arko_key(self):
        with patch.dict(
            os.environ,
            {
                "KOFIC_BOX_OFFICE_SERVICE_KEY": "kofic-secret",
                "ARKO_EVENT_SERVICE_KEY": "arko-secret",
                "MCST_PERFORMANCE_SERVICE_KEY": "mcst-secret",
            },
            clear=True,
        ):
            settings = ArkoEventSettings.from_env()

        self.assertEqual("arko-secret", settings.service_key.raw_key)

    def test_mcst_settings_require_mcst_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(McstPerformanceError):
                McstPerformanceSettings.from_env()

    def test_mcst_settings_read_only_mcst_key(self):
        with patch.dict(
            os.environ,
            {
                "KOFIC_BOX_OFFICE_SERVICE_KEY": "kofic-secret",
                "ARKO_EVENT_SERVICE_KEY": "arko-secret",
                "MCST_PERFORMANCE_SERVICE_KEY": "mcst-secret",
            },
            clear=True,
        ):
            settings = McstPerformanceSettings.from_env()

        self.assertEqual("mcst-secret", settings.service_key.raw_key)


if __name__ == "__main__":
    unittest.main()
