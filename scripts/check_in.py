#!/usr/bin/env python3
"""Create up to ten explicitly automated check-ins per Shanghai calendar day."""
from datetime import datetime
from pathlib import Path
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
        expected = header
        for count in range(11):
            if contents == expected:
                completed = count
                break
            expected += f"- Automated check-in {count + 1:02d}/10\n"
        else:
            raise SystemExit(f"Unexpected content in {path}; refusing to overwrite.")
    else:
        contents = header
    path.parent.mkdir(parents=True, exist_ok=True)
    for count in range(completed + 1, 11):
        contents += f"- Automated check-in {count:02d}/10\n"
        path.write_text(contents, encoding="utf-8")
        git("add", "--", str(path))
        git("commit", "-m", f"chore: automated check-in {day} ({count:02d}/10)")
    print(f"{day}: created {10 - completed} commits; 10/10 check-ins complete.")


if __name__ == "__main__":
    main()
