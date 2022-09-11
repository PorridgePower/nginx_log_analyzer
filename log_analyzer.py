#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
from os import listdir, path
from collections import namedtuple
from urlparse import urlparse
import time
import re

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

LOG_RECORD_PATTERN = (
    r'^(?P<remote_addr>[\d.]{7,15}) (?P<remote_user>[\S]+)  (?P<http_x_real_ip>[\d.-]+) '
    r'\[(?P<time_local>).*\] "(?P<request>.+)" (?P<status>\d{3}) (?P<body_bytes_sent>[-\d]+) '
    r'"(?P<http_referer>[\S]+)" "(?P<http_user_agent>.+)" "(?P<http_x_forwarded_for>[\S]+)" '
    r'"(?P<http_X_REQUEST_ID>[\S]+)" "(?P<http_X_RB_USER>[\S]+)" (?P<request_time>[\d\.]+)'
)

config = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log"}
LogInfo = namedtuple("Logfile", ["logfile", "extention", "date"])


def get_latest_log(logdir):
    latest_date = 0
    filename = None
    ext = None
    for f in listdir(logdir):
        s = re.search("(nginx-access-ui\.log-([\d]{8})\.(log|gz))", f)
        if s is None:
            continue
        day_str = s.group(2)
        day = time.strptime(day_str, "%Y%m%d")
        if day > latest_date:
            latest_date = day
            filename = s.group(1)
            ext = s.group(3)
    return LogInfo(path.join(logdir, filename), ext, latest_date)


def parse_log(logfile, extention):
    opener = gzip.open if extention == 'gz' else open
    with opener(logfile, "rb") as log:
        for line in log:
            yield parse_record(line.decode('utf-8'))


def parse_record(record):
    expression = re.compile(LOG_RECORD_PATTERN)
    parse_result = expression.search(record)
    print(record)
    if parse_result is None:
        return (None, ) * 2
    else:
        request_path = urlparse(parse_result.group("request").split()[1]).path
        request_time = parse_result.group("request_time")
        return (request_path, request_time)


def main():
    pass

if __name__ == "__main__":
    main()
