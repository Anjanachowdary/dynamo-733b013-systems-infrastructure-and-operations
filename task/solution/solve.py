#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

LOG_PATH = Path("/app/access.log")
REPORT_PATH = Path("/app/report.json")


def main() -> None:
    total = 0
    ips = set()
    paths = Counter()

    with LOG_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            total += 1
            parts = line.split()
            if parts:
                ips.add(parts[0])
            quoted = line.split('"')[1]
            request_parts = quoted.split()
            if len(request_parts) >= 2:
                paths[request_parts[1]] += 1

    top_path = paths.most_common(1)[0][0] if paths else ""
    payload = {
        "total_requests": total,
        "unique_ips": len(ips),
        "top_path": top_path,
    }
    REPORT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
