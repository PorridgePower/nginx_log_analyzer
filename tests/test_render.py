import unittest
from os import path, remove
from time import strptime
from log_analyzer import render_report


class TestReportGereration(unittest.TestCase):
    testrep = path.join(
        path.dirname(path.abspath(__file__)), "testdir", "report000.html"
    )
    data = [
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
    ]

    def test_file_generation(self):
        render_report(self.data, self.testrep, 10),
        self.assertEqual(path.exists(self.testrep), True)

    def tearDown(self):
        remove(self.testrep)
