import unittest
from log_analyzer import parse_record


class TestParsing(unittest.TestCase):
    def test_invalid_record(self):
        record = '- -  - [-] "-" - - "-" "-" "-" "-" "-" -'
        self.assertEqual(parse_record(record), (None, None))

    def test_valid_record(self):
        record = (
            "1.194.135.240 -  - [29/Jun/2017:03:50:23 +0300] "
            '"GET /api/v2/group/7786682/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28 HTTP/1.1" '
            '200 22 "-" "python-requests/2.13.0" "-" "1498697423-3979856266-4708-9752778" "8a7741a54297568b" 0.068'
        )

        self.assertEqual(
            parse_record(record), ("/api/v2/group/7786682/statistic/sites/", "0.068")
        )


if __name__ == "__main__":
    unittest.main()
