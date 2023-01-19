#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
from os import listdir, path
from collections import namedtuple
from urllib.parse import urlparse
import time
import re
import argparse
import configparser
from decimal import Decimal
from string import Template
import statistics
import logging

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

LOG_RECORD_PATTERN = (
    r"^(?P<remote_addr>[\d.]{7,15}) (?P<remote_user>[\S]+)  (?P<http_x_real_ip>[\d.-]+) "
    r'\[(?P<time_local>).*\] "(?P<request>.+)" (?P<status>\d{3}) (?P<body_bytes_sent>[-\d]+) '
    r'"(?P<http_referer>[\S]+)" "(?P<http_user_agent>.+)" "(?P<http_x_forwarded_for>[\S]+)" '
    r'"(?P<http_X_REQUEST_ID>[\S]+)" "(?P<http_X_RB_USER>[\S]+)" (?P<request_time>[\d\.]+)'
)

CONFIG = {
    "REPORT_SIZE": "1000",
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "OUTPUT": None,
}
LogInfo = namedtuple("Logfile", ["logfile", "extention", "date"])


def init_configuration(default_conf, specified_conf):
    """Reads and merges configurations

    Args:
        default_conf (dict): Dafault configuration
        specified_conf (str): User specified path to .conf file

    Returns:
        dict: Result configuration
    """
    if path.exists(specified_conf):
        config_parser = configparser.ConfigParser(allow_no_value=True)
        try:
            config_parser.read(specified_conf)
        except configparser.Error:
            logging.warning("Cannot read specified conf file. Using default config")
            return default_conf
        merged_conf = {}
        for k in default_conf.keys():
            merged_conf[k] = config_parser.get("PARAMS", k, fallback=default_conf[k])
        return merged_conf
    else:
        return default_conf


def get_latest_log(logdir):
    """Gets path for latest Nginx logfile (by date in filename)

    Args:
        logdir (str): Path for log search

    Returns:
        LogInfo: Named tuple (path, extention, date) of latest log or None
    """
    latest_date = time.gmtime(0)
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
    return LogInfo(path.join(logdir, filename), ext, latest_date) if filename else None


def parse_log(logfile, extention):
    """Opens logfile and generates parsed data

    Args:
        logfile (str): Path to logfile
        extention (str): Type of log file - "gz" or "log"

    Yields:
        str: Data parsed frol log line
    """
    opener = gzip.open if extention == "gz" else open
    with opener(logfile, "rb") as log:
        for line in log:
            yield parse_record(line.decode("utf-8"))


def parse_record(record):
    """Extract data fields (request URL and time) from log line

    Args:
        record (str): Log line

    Returns:
        tuple: Request URL, estimated time or (None,None)
    """
    expression = re.compile(LOG_RECORD_PATTERN)
    parse_result = expression.search(record)
    if parse_result is None:
        return (None,) * 2
    else:
        try:
            request_path = urlparse(parse_result.group("request").split()[1]).path
        except:
            return (None,) * 2
        request_time = parse_result.group("request_time")
        return (request_path, request_time)


def process(configuration):
    """Processes configurations and starts parising

    Args:
        configuration (dict): Merged configuration
    """
    if not path.exists(configuration["LOG_DIR"]):
        logging.error("Log directory %s does not exist." % configuration["LOG_DIR"])
        return
    if not path.exists(configuration["REPORT_DIR"]):
        logging.error(
            "Reports directory %s does not exist." % configuration["REPORT_DIR"]
        )
        return

    logfile = get_latest_log(configuration["LOG_DIR"])
    if not logfile:
        logging.error("Suitable log file not found")
        return
    reportname = path.join(
        configuration["REPORT_DIR"],
        "report-%s.html" % time.strftime("%Y.%m.%d", logfile.date),
    )

    if path.exists(reportname):
        logging.info("Report was previosly generated and saved in %s" % reportname)
        return

    try:
        size = int(configuration["REPORT_SIZE"])
    except ValueError:
        logging.error("Incorrect REPORT_SIZE value")
        return

    data = generate_statistics(logfile)
    sorted_data = sorted(data, key=lambda d: float(d["time_sum"]), reverse=True)
    render_report(sorted_data, reportname, size)


def generate_statistics(log):
    """Calculates stat and generates result table

    Args:
        log (str): Path to logfile

    Returns:
        list: Result table
    """
    logging.info("Parsing %s" % log.logfile)
    total_requests = 0
    total_time = 0
    table = []
    for url, times in select_times(log).items():
        url_time = Decimal(sum(times))
        url_count = len(times)
        time_avg = Decimal(url_time / len(times))
        time_max = max(times)
        time_med = statistics.median(times)
        table.append(
            {
                "url": url,
                "count": url_count,
                "time_sum": url_time,
                "time_avg": time_avg.to_eng_string(),
                "time_max": time_max.to_eng_string(),
                "time_med": time_med.to_eng_string(),
            }
        )
        total_requests += url_count
        total_time += url_time

    for url_data in table:
        url_data["count_perc"] = str(url_data["count"] / total_requests)
        url_data["time_perc"] = str(url_data["time_sum"] / total_time)
        url_data["time_sum"] = url_data["time_sum"].to_eng_string()

    return table


def select_times(log):
    """Accumulates all request times for each url in log

    Args:
        log (str): Path to logfile

    Returns:
        dict: Urls with request times
    """
    errors = 0
    time_stat = {}
    for url, req_time in parse_log(log.logfile, log.extention):
        if url is None:
            errors += 1
            continue
        if not url in time_stat.keys():
            time_stat[url] = []
        time_stat[url].append(Decimal(req_time))
    return time_stat


def render_report(url_data, report_fname, report_size):
    """Insert table to report temlate

    Args:
        url_data (list): Data to render
        report_fname (str): Path to report file
        report_size (int): Count of lines of table to render
    """
    template_fname = path.join(
        path.dirname(path.realpath(__file__)), "templates", "report.html"
    )
    if not path.exists(template_fname):
        logging.error(f"File {template_fname} not found.  Aborting")
        return
    try:
        with open(template_fname, "r") as template:
            s = Template(template.read())
            res = s.substitute(table_json=url_data[:report_size])
            with open(report_fname, "wb") as report:
                report.write(res.encode("utf-8"))
    except IOError:
        logging.exception(
            "Error while preparing report", exc_info=True, stack_info=True
        )
        return
    except ValueError:
        logging.exception("Error while filling report", exc_info=True, stack_info=True)
        return
    logging.info("Report written to %s" % report_fname)


def init_logging(output=None):
    logging.basicConfig(
        filename=output,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Analyses Nginx log for most requested URLs and generate report"
    )
    parser.add_argument(
        "--conf",
        metavar="conf_file",
        type=str,
        default="",
        help="Configuration file",
        required=False,
    )

    args = parser.parse_args()

    current_conf = init_configuration(default_conf=CONFIG, specified_conf=args.conf)
    init_logging(current_conf["OUTPUT"])

    logging.info(
        "Current configuration: \n%s"
        % "\n".join(f"{k}={v}" for k, v in current_conf.items())
    )

    process(current_conf)


if __name__ == "__main__":
    main()
