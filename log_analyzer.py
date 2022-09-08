#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
from os import listdir, path
import time
import re

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def get_latest_log(logdir):
    latest_date = 0
    filename = None
    ext = None
    for f in listdir(logdir):
        s = re.search("(nginx-access-ui\.log-([\d]{8})\.(log|gz))", f)
        day_str = s.group(2)
        filename = s.group(1)
        ext = s.group(3)
        day = time.strptime(day_str, "%Y%m%d")
        if day > latest_date:
            latest_date = day
    return {
        "logfile": path.join(logdir, filename),
        "extention": ext,
        "date": latest_date
    }


def open_log(logfile, extention):
    opener = gzip.open if extention == 'gz' else open

    with opener(logfile, "rb") as log:
        for record in log:
            yield record.decode('utf-8')


def main():
    pass

if __name__ == "__main__":
    main()
