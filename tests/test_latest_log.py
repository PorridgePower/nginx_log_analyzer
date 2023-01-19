import unittest
from os import path
from time import strptime
from log_analyzer import get_latest_log, LogInfo


class TestLatestLogSearch(unittest.TestCase):
    def setUp(self):
        self.testdir = path.join(path.dirname(path.abspath(__file__)), "testdir")

    def test_valid_name(self):
        self.assertEqual(
            get_latest_log(self.testdir),
            LogInfo(
                path.join(self.testdir, "nginx-access-ui.log-20220909.gz"),
                "gz",
                strptime("20220909", "%Y%m%d"),
            ),
        )

    def test_empty_dir(self):
        self.assertEqual(get_latest_log(path.join(self.testdir, "empty")), None)


if __name__ == "__main__":
    unittest.main()
