"""Select final upstream releases; workflow owns git and PR mutations."""
import json
import re
import subprocess


def choose_release(releases, current=(0, 23, 1)):
    candidates = []
    for release in releases:
        tag = release.get('tag_name', '')
        match = re.fullmatch(r'v(0|[1-9][0-9]{0,2})\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', tag)
        if match and not release.get('prerelease') and not release.get('draft'):
            version = tuple(map(int, match.groups()))
            if version > current:
                candidates.append((version, tag))
    return max(candidates)[1] if candidates else None


if __name__ == '__main__':
    result = subprocess.run(['gh','api','repos/NousResearch/hermes-agent/releases?per_page=100'], check=True, capture_output=True, text=True)
    print(choose_release(json.loads(result.stdout)) or '')
