"""Summarize Court Automation's script calls in CK3's Script.Profiling.Export CSV."""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re


def summarize(path: Path) -> dict:
    data = path.read_bytes()
    lines = data.decode('utf-8-sig').splitlines()
    headers = [line for line in lines if line.startswith('#')]
    capture = re.search(r'\bticks=(\d+)\s+frames=(\d+)\s+collected_time=([\d.]+)', '\n'.join(headers))
    if not capture or int(capture[2]) < 1:
        raise ValueError(f'Missing frame count in {path}')
    ticks, frames = int(capture[1]), int(capture[2])
    rows = csv.DictReader(line for line in lines if line and not line.startswith('#'))
    if not {'file', 'line', 'call_count'} <= set(rows.fieldnames or ()):
        raise ValueError(f'Unrecognized profiler columns in {path}')

    calls = Counter()
    exclusions = Counter()
    entries = 0
    for row in rows:
        entries += 1
        file = row['file'].replace('\\', '/').rsplit('/', 1)[-1]
        if file.startswith('ca_') and file.endswith('.txt'):
            count = int(row['call_count'])
            calls[file] += count
            if file == 'ca_position_exclusion_guis.txt':
                exclusions[row['line']] += count
    if not entries:
        raise ValueError(f'Empty profile in {path}')
    return {
        'capture': str(path), 'sha256': hashlib.sha256(data).hexdigest(),
        'frames': frames, 'ticks': ticks, 'capture_seconds': float(capture[3]),
        'script_calls_by_file': dict(calls.most_common()),
        'exclusion_calls_by_line': dict(exclusions),
    }


def summarize_series(paths):
    """Export keeps earlier counters in this process, but reports the latest window's frames."""
    previous_files = {}
    previous_lines = {}
    results = []
    for index, path in enumerate(paths):
        if path.name != f'script_profile_{index:03d}.csv' or path.parent != paths[0].parent:
            raise ValueError('Supply consecutive exports from one process, starting at 000')
        capture = summarize(path)
        files = capture.pop('script_calls_by_file')
        lines = capture.pop('exclusion_calls_by_line')
        def increment(after, before):
            diff = {name: after.get(name, 0) - before.get(name, 0) for name in after.keys() | before.keys()}
            if any(n < 0 for n in diff.values()):
                raise ValueError(f'Profiler counters decreased at {path}')
            return dict(sorted(diff.items()))
        file_calls = increment(files, previous_files)
        line_calls = increment(lines, previous_lines)
        capture['script_calls_by_file'] = file_calls
        capture['exclusion_calls_by_line'] = line_calls
        capture['exclusion_line_31_calls_per_frame'] = round(line_calls.get('31', 0) / capture['frames'], 2)
        capture['exclusion_file_calls_per_frame'] = round(sum(line_calls.values()) / capture['frames'], 2)
        results.append(capture)
        previous_files, previous_lines = files, lines
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('captures', nargs='+', type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize_series(args.captures), indent=2))
