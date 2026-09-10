#!/usr/bin/env python3
"""Create a random 1–10 automated check-ins per Shanghai calendar day."""
from datetime import datetime
from pathlib import Path
from random import randint
import re
import subprocess
from zoneinfo import ZoneInfo


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def main():
    if git("status", "--porcelain"):
        raise SystemExit("Working tree must be clean before check-in.")
    day = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    path = Path("activity") / f"{day}.md"
    header = f"# {day}\n\nAutomated daily check-ins (Asia/Shanghai).\n\n"
    completed = 0
    if path.exists():
        contents = path.read_text(encoding="utf-8")
        if not contents.startswith(header):
            raise SystemExit(f"Unexpected header in {path}; refusing to overwrite.")
        entries = contents[len(header):]
        first = re.match(r"- Automated check-in 01/(0[1-9]|10)\n", entries)
        # The first committed entry persists the target across retries.
        # Legacy files used /10; a legacy header-only file also retains 10.
        if entries and not first:
            raise SystemExit(f"Unexpected content in {path}; refusing to overwrite.")
        target = int(first.group(1)) if first else 10
        expected = header
        for count in range(target + 1):
            if contents == expected:
                completed = count
                break
            expected += f"- Automated check-in {count + 1:02d}/{target:02d}\n"
        else:
            raise SystemExit(f"Unexpected content in {path}; refusing to overwrite.")
    else:
        target = randint(1, 10)
        contents = header
    path.parent.mkdir(parents=True, exist_ok=True)
    for count in range(completed + 1, target + 1):
        contents += f"- Automated check-in {count:02d}/{target:02d}\n"
        path.write_text(contents, encoding="utf-8")
        git("add", "--", str(path))
        git("commit", "-m", f"chore: automated check-in {day} ({count:02d}/{target:02d})")
    print(f"{day}: created {target - completed} commits; {target}/{target} check-ins complete.")


if __name__ == "__main__":
    main()
