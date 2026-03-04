#!/usr/bin/env python3
"""Fetch FEMA IPAWS archived alerts and save to JSONL.

Usage examples:
	python scripts/access_ipaws_archive.py --output data/raw/ipaws_archived_alerts.jsonl
	python scripts/access_ipaws_archive.py --url https://www.fema.gov/api/open/v1/IpawsArchivedAlerts --max 100

The script uses only the Python standard library so no extra dependencies are required.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Iterable, Optional

try:
	from urllib.request import urlopen, Request
	from urllib.parse import urlencode
except Exception:
	raise


DEFAULT_URL = "https://www.fema.gov/api/open/v1/IpawsArchivedAlerts"


def fetch_pages(url: str, params: Optional[Dict[str, Any]] = None) -> Iterable[Any]:
	"""Yield items from the FEMA endpoint, following common next-link fields."""
	params = params or {}
	if params:
		sep = "&" if "?" in url else "?"
		url = f"{url}{sep}{urlencode(params)}"

	while url:
		req = Request(url, headers={"User-Agent": "access_ipaws_archive/1.0"})
		with urlopen(req, timeout=30) as resp:
			text = resp.read().decode("utf-8")
			try:
				data = json.loads(text)
			except Exception:
				return

		if isinstance(data, dict):
			if "value" in data and isinstance(data["value"], list):
				for item in data["value"]:
					yield item
				next_url = None
				for key in ("@odata.nextLink", "odata.nextLink", "next"):
					if key in data and data[key]:
						next_url = data[key]
						break
				if not next_url and "_links" in data and isinstance(data["_links"], dict):
					nxt = data["_links"].get("next")
					if isinstance(nxt, dict) and "href" in nxt:
						next_url = nxt["href"]
				url = next_url
			else:
				yield data
				url = None
		elif isinstance(data, list):
			for item in data:
				yield item
			url = None
		else:
			return

		time.sleep(0.1)


def write_jsonl(items: Iterable[Any], out_path: str, max_records: Optional[int] = None, pretty: bool = False) -> int:
	os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

	records = []
	for obj in items:
		if max_records is not None and len(records) >= max_records:
			break
		records.append(obj)

	# Save as a single formatted JSON array (not JSONL)
	with open(out_path, "w", encoding="utf-8") as fh:
		json.dump(records, fh, ensure_ascii=False, indent=2)
		fh.write("\n")

	return len(records)


def main(argv: Optional[list[str]] = None) -> int:
	p = argparse.ArgumentParser(description="Fetch FEMA IPAWS archived alerts and save JSON.")
	p.add_argument("--url", default=DEFAULT_URL, help="FEMA API URL")
	p.add_argument("--output", "-o", default="data/raw/ipaws_archived_alerts.jsonl", help="Output path")
	p.add_argument("--max", type=int, default=10, help="Maximum number of records to fetch")
	p.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
	args = p.parse_args(argv)

	try:
		# Request newest first from OData-compatible API
		params: Dict[str, Any] = {"$orderby": "sent desc"}
		if args.max is not None:
			params["$top"] = args.max

		items = fetch_pages(args.url, params=params)
		n = write_jsonl(items, args.output, max_records=args.max, pretty=args.pretty)
	except KeyboardInterrupt:
		print("Interrupted", file=sys.stderr)
		return 2
	except Exception as exc:
		print(f"Error: {exc}", file=sys.stderr)
		return 1

	print(f"Wrote {n} records to {args.output}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
