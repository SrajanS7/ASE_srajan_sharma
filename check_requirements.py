"""Check every line of a requirements.txt against the PyPI JSON API."""

import json
import sys
import urllib.error
import urllib.request

PYPI = "https://pypi.org/pypi"


def fetch_json(url):
    """Return the parsed JSON at url, or None if PyPI answers 404."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def main(path):
    with open(path) as f:
        lines = [line.strip() for line in f if line.strip()]

    missing_packages = 0
    missing_versions = 0
    oldest = None  # (upload_time, "name==version")

    for line in lines:
        name, version = line.split("==")

        if fetch_json(f"{PYPI}/{name}/json") is None:
            missing_packages += 1
            continue

        release = fetch_json(f"{PYPI}/{name}/{version}/json")
        if release is None:
            missing_versions += 1
            continue

        # upload_time is ISO format (e.g. "2019-01-14T04:35:07"), so string comparison sorts by date
        upload_time = release["urls"][0]["upload_time"]
        if oldest is None or upload_time < oldest[0]:
            oldest = (upload_time, line)

    print(f"Dependencies checked: {len(lines)}")
    print(f"Packages not on PyPI: {missing_packages}")
    print(f"Versions not on PyPI: {missing_versions}")
    if oldest:
        print(f"Oldest pinned release: {oldest[1]} ({oldest[0][:4]})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "requirements.txt")
