import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
SKIP = {".venv", ".git", "__pycache__", "node_modules", "models"}
EXT = {".py", ".toml", ".txt", ".md", ".csv", ".bat", ".sh", ".json", ".gitignore"}
START, MID, END = re.compile(r"^<<<<<<<( .*)?$"), re.compile(r"^=======$"), re.compile(r"^>>>>>>>( .*)?$")
STRAY = re.compile(r"^[0-9a-f]{7,} \(.*\)$")


def clean(text):
    out, state, removed = [], 0, 0
    for line in text.splitlines(keepends=True):
        s = line.rstrip("\r\n")
        if START.match(s):
            state, removed = 1, removed + 1
        elif state == 1 and MID.match(s):
            state, removed = 2, removed + 1
        elif state in (1, 2) and (END.match(s) or STRAY.match(s)):
            state, removed = 0, removed + 1
        elif STRAY.match(s):
            removed += 1
        elif state != 2:
            out.append(line)
        else:
            removed += 1
    return "".join(out), removed


fixed = 0
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or set(p.parts) & SKIP or (p.suffix not in EXT and p.name != ".gitignore"):
        continue
    try:
        old = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    new, removed = clean(old)
    if new != old:
        p.with_name(p.name + ".bak").write_text(old, encoding="utf-8", newline="")
        p.write_text(new, encoding="utf-8", newline="")
        fixed += 1
        print(f"fixed {p.relative_to(ROOT)}: removed {removed} conflict line(s)")
print(f"\nDone. {fixed} file(s) repaired." if fixed else "\nNo conflict markers found.")