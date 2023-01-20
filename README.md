# Nginx Log Analyzer

Nginx Log Analyzer is a simple script for analyzing Nginx logfiles.

and preparing an html-report with statistics of  requetst time for aech resource.

## Requirements

Need only Python 3.

## Usage

Run `./log_analyzer.py` or `./log_analyzer.py --help` to get a bit more info.

```
log_analyzer.py [-h] [--conf conf_file]

Analyses Nginx log for most requested URLs and generate report

optional arguments:
  -h, --help        show this help message and exit
  --conf conf_file  Configuration file
```

### Configuration

```
[PARAMS]
REPORT_SIZE=<count entries(url) in report>
REPORT_DIR=<path where reports should be located>
LOG_DIR=<path to directory with logs>
OUTPUT=<filename for script output or None to use stdout>
```

In case no configuration file was provided, the script uses following params as default:

REPORT_SIZE = 1000

REPORT_DIR = ./reports

LOG_DIR = ./log

OUTPUT = None (stdout)

### Log format

Script work correct with next Nginx log format:

```
$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" 
$status $body_bytes_sent "$http_referer" "$http_user_agent" "$http_x_forwarded_for" 
"$http_X_REQUEST_ID" "$http_X_RB_USER" '$request_time';
```

You also able to chenge regexp for parsing by redefine pattern `LOG_RECORD_PATTERN` if it's necessary.

If > 70% of the log file cannot be parsed, no report will be generated.

### Result Examples

There is the result table sample:

<img width="1440" alt="image" src="https://user-images.githubusercontent.com/62947325/213805174-c1899f20-7608-4014-a654-cb97df370e9f.png">

Report includex next columns:
* *url*: Requested URL path (parameters are discarded)
* *count*: Total requests to given URL
* *count_perc*: Relative percentage of requests to given URL
                from the total number of requests
* *time_avg*: Average request time to given URL
* *time_max*: Max request time to given URL
* *time_med*: Median value of request time to given URL
* *time_perc*: Relative percentage of request time to given URL 
               from the total elapsed time
* *time_sum*: Summary request time to given URL

## Run tests

Run all tests
```
python3 -m unittest
```