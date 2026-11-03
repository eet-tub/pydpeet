"""Fetch the Vebtan ``failedFiles`` table and print/write a report grouped by failure reason.

1. request every page of ``http://130.149.179.21/database/failedFiles?rows=1000&page=N``
   and read the failed-file table directly from there,
2. group the entries by their individual failure reason,
3. print and write a plain-text report listing each reason, how often it occurs and the
   first file (with its id) that failed with it,
4. download the first file of every failure-reason group into ``failed_files/``;
   downloads are rejected once the folder-size limit is reached and the remaining
   code still runs.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Hashable
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

BASE_URL = "http://130.149.179.21/database/failedFiles?rows=1000&page={page}"
DOWNLOAD_API_URL = "http://130.149.179.21/api/download"
REPORT_PATH = Path(__file__).resolve().parent / "failed_files.txt"
DOWNLOAD_DIR = Path(__file__).resolve().parent / "failed_files"
FOLDER_SIZE_LIMIT = 10 * 1024**3  # 10 GB

# Failure reasons that are considered an acceptable, expected outcome, tagged as such in the report.
FAILED_SUCCESSFULLY = [
    "File type must be TXT or CSV.",
]


def fetch_html(url: str) -> str:
    """Fetch ``url`` and return the decoded response body."""
    with urlopen(url) as response:  # noqa: S310 - fixed, trusted internal host
        return response.read().decode(response.headers.get_content_charset() or "utf-8")


def rsc_payload(html: str) -> str:
    """Reassemble the React Server Component payload from the Next.js HTML."""
    return "".join(
        json.loads(match) for match in re.compile(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)').findall(html)
    )


def _records(payload: str) -> list[dict[str, Any]]:
    """Return the failed-file records from a single page's RSC payload."""
    table_index = payload.find('"table":"failedFiles"')
    if table_index == -1:
        return []
    data_index = payload.find('"data":', table_index)
    if data_index == -1:
        return []
    try:
        array_start = payload.index("[", data_index)
        records, _ = json.JSONDecoder().raw_decode(payload, array_start)
    except ValueError:
        return []
    return records


def download_records() -> list[dict[str, Any]]:
    """Download every page and return the de-duplicated failed-file records."""
    entries: list[dict[str, Any]] = []
    seen: set[Any] = set()
    total: int | None = None
    page = 1
    while True:
        html = fetch_html(BASE_URL.format(page=page))
        payload = rsc_payload(html)
        page_records = _records(payload)
        if not page_records:
            break

        new_records = 0
        for entry in page_records:
            entry_id = entry.get("id")
            if isinstance(entry_id, Hashable) and entry_id in seen:
                continue
            if isinstance(entry_id, Hashable):
                seen.add(entry_id)
            entries.append(entry)
            new_records += 1

        if total is None:
            match = re.search(r'"pageFilter":\{"total":(\d+)', payload)
            total = int(match.group(1)) if match else None
        print(f"Downloaded page {page}: {new_records} new records ({len(entries)}/{total or '?'}).")

        if new_records == 0 or (total is not None and len(entries) >= total):
            break
        page += 1
    return entries


def group_by_reason(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group failed-file records by their individual failure reason."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        error = entry.get("error")
        reason = str(error.get("error", error)) if isinstance(error, dict) else str(error)
        groups[reason].append(entry)
    return groups


def write_report(entries: list[dict[str, Any]], path: Path = REPORT_PATH) -> Path:
    """Print and store the failures grouped by reason in a plain-text report."""
    groups = group_by_reason(entries)

    blocks = []
    for reason, records in sorted(groups.items(), key=lambda item: len(item[1]), reverse=True):
        first = records[0]
        raw_files = first.get("rawFiles") or []
        first_file = str(raw_files[0]) if raw_files else ""
        tag = "Tag: failed successfully\n" if reason in FAILED_SUCCESSFULLY else ""
        blocks.append(
            f"Error: {reason}\n"
            f"{tag}"
            f"Number of occurrences: {len(records)}\n"
            f"First file with said Error: {first_file} , {first.get('id')}"
        )
    text = "\n\n".join(blocks) + "\n"
    print(text, end="")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def download_file(record_id: Any) -> tuple[str, bytes]:
    """Download the ``rawFiles`` content of one ``failedFiles`` row.

    Returns the original filename (from ``Content-Disposition``) and the raw bytes.
    """
    payload = json.dumps({"table": "failedFiles", "column": "rawFiles", "rows": [{"id": record_id}]}).encode()
    request = Request(
        DOWNLOAD_API_URL,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=120) as response:  # noqa: S310 - fixed, trusted internal host
        body = response.read()
        disposition = response.headers.get("Content-Disposition") or ""
    match = re.search(r'filename="([^"]+)"', disposition)
    filename = Path(match.group(1)).name if match else str(record_id)
    return filename, body


def download_first_occurrences(
    groups: dict[str, list[dict[str, Any]]],
    folder: Path = DOWNLOAD_DIR,
    limit: int = FOLDER_SIZE_LIMIT,
) -> tuple[int, int, int]:
    """Download the first record of every failure-reason group into ``folder``.

    Files are stored as ``<id>-<original filename>``. Once ``limit`` bytes have
    been downloaded, every remaining download is rejected; the rest of the code
    (skipped counting, summary) still runs.

    Returns ``(downloaded, skipped, total_size)``.
    """
    folder.mkdir(parents=True, exist_ok=True)
    ordered = sorted(groups.items(), key=lambda item: len(item[1]), reverse=True)
    downloaded = 0
    skipped = 0
    total_size = 0

    for index, (reason, records) in enumerate(ordered):
        if total_size >= limit:
            rejected = len(ordered) - index
            print(
                f"Folder size limit of {limit} bytes reached ({total_size} bytes used): "
                f"rejecting {rejected} remaining download(s)."
            )
            skipped += rejected
            break

        first = records[0]
        record_id = first.get("id")
        raw_files = first.get("rawFiles") or []
        if record_id is None or not raw_files:
            print(f"Skipping (missing id or rawFiles): {reason}")
            skipped += 1
            continue

        try:
            filename, content = download_file(record_id)
        except (URLError, OSError, ValueError) as error:
            print(f"Download failed for id {record_id} ({reason}): {error}")
            skipped += 1
            continue

        target = folder / f"{record_id}-{filename}"
        target.write_bytes(content)
        total_size += len(content)
        downloaded += 1
        print(f"Downloaded {target.name} ({len(content)} bytes) -> {total_size}/{limit} bytes used.")

    print(f"{downloaded} file(s) downloaded, {skipped} skipped/rejected -> {folder}")
    return downloaded, skipped, total_size


if __name__ == "__main__":
    entries = download_records()
    report = write_report(entries)
    print(f"\n{len(entries)} failed files -> {report}")
    download_first_occurrences(group_by_reason(entries))
