import unittest
from os import path
from log_analyzer import init_configuration, CONFIG


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.testdir = path.join(path.dirname(path.abspath(__file__)), "testdir")

    def test_not_existing_file(self):
        self.assertEqual(
            init_configuration(
                default_conf=CONFIG,
                specified_conf=path.join(self.testdir, "not_existing.conf"),
            ),
            CONFIG,
        )

    def test_invalid_config(self):
        self.assertEqual(
            init_configuration(
                default_conf=CONFIG,
                specified_conf=path.join(self.testdir, "invalid.conf"),
            ),
            CONFIG,
        )

    def test_merge(self):
        self.assertEqual(
            init_configuration(
                default_conf=CONFIG,
                specified_conf=path.join(self.testdir, "valid.conf"),
            ),
            {
                "REPORT_SIZE": "100",
                "REPORT_DIR": "./test_reports",
                "OUTPUT": None,
                "LOG_DIR": "./log",
            },
        )


if __name__ == "__main__":
    unittest.main()
