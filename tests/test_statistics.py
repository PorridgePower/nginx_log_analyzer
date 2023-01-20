import unittest
from os import path
import time
from decimal import Decimal
from log_analyzer import select_times, generate_statistics, LogInfo


class TestCalculations(unittest.TestCase):
    testdir = path.join(path.dirname(path.abspath(__file__)), "testdir")

    def test_hreshold_limit(self):
        self.assertEqual(
            select_times(
                LogInfo(path.join(self.testdir, "errors.log"), "log", time.gmtime(0))
            ),
            {},
        )

    def test_select(self):
        self.assertEqual(
            select_times(
                LogInfo(path.join(self.testdir, "valid.log.gz"), "gz", time.gmtime(0))
            ),
            {
                "/api/v2/group/5775925/banners": [Decimal("0.626")],
                "/export/appinstall_raw/": [
                    Decimal("0.002"),
                    Decimal("0.001"),
                    Decimal("0.003"),
                    Decimal("0.001"),
                ],
                "/api/v2/banner/": [
                    Decimal("0.156"),
                    Decimal("3.009"),
                    Decimal("0.153"),
                    Decimal("0.624"),
                    Decimal("0.269"),
                    Decimal("0.169"),
                ],
                "/api/1/campaigns/": [
                    Decimal("0.179"),
                    Decimal("0.150"),
                    Decimal("0.156"),
                ],
            },
        )

    def test_empty_statistics(self):
        self.assertEqual(
            generate_statistics(
                LogInfo(path.join(self.testdir, "errors.log"), "log", time.gmtime(0))
            ),
            [],
        )

    def test_statistics(self):
        self.assertEqual(
            generate_statistics(
                LogInfo(path.join(self.testdir, "valid.log.gz"), "gz", time.gmtime(0))
            ),
            [
                {
                    "url": "/api/v2/group/5775925/banners",
                    "count": 1,
                    "time_sum": "0.626",
                    "time_avg": "0.626",
                    "time_max": "0.626",
                    "time_med": "0.626",
                    "count_perc": "0.07142857142857142",
                    "time_perc": "0.1138595853037468170243724991",
                },
                {
                    "url": "/export/appinstall_raw/",
                    "count": 4,
                    "time_sum": "0.007",
                    "time_avg": "0.00175",
                    "time_max": "0.003",
                    "time_med": "0.0015",
                    "count_perc": "0.2857142857142857",
                    "time_perc": "0.001273190251000363768643142961",
                },
                {
                    "url": "/api/v2/banner/",
                    "count": 6,
                    "time_sum": "4.380",
                    "time_avg": "0.730",
                    "time_max": "3.009",
                    "time_med": "0.219",
                    "count_perc": "0.42857142857142855",
                    "time_perc": "0.7966533284830847580938523099",
                },
                {
                    "url": "/api/1/campaigns/",
                    "count": 3,
                    "time_sum": "0.485",
                    "time_avg": "0.1616666666666666666666666667",
                    "time_max": "0.179",
                    "time_med": "0.156",
                    "count_perc": "0.21428571428571427",
                    "time_perc": "0.08821389596216806111313204802",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
