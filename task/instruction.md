There is an Apache-style access log at /app/access.log. Each line is one HTTP request, in the standard combined-log style, e.g.:

192.168.0.1 - - [16/Jun/2026:10:00:01 +0000] "GET /index.html HTTP/1.1" 200 1024

Parse the log and write a summary report as JSON to /app/report.json, with exactly these three fields:

- total_requests: the total number of requests (lines) in the log.
- unique_ips: the number of distinct client IP addresses that appear in the log.
- top_path: the request path (the second token inside the quoted request, e.g. /index.html) that appears most often across all requests.

Success criteria:
1. /app/report.json exists and contains valid JSON.
2. total_requests exactly equals the number of requests in /app/access.log.
3. unique_ips exactly equals the number of distinct client IP addresses in /app/access.log.
4. top_path exactly equals the most frequently requested path in /app/access.log.
