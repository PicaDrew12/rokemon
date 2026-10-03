 
#!/usr/bin/env python3
"""Replace characters that are NOT in charmap.txt, inside C string literals
(code only, not comments), with '?'. One char -> one char, so byte lengths
and padding stay identical. Run from the pokeemerald root.
Usage: python3 strip_jp.py [--apply]   (without --apply it only reports)"""
import re, sys, pathlib

apply = "--apply" in sys.argv
known = set()
for line in open("charmap.txt", encoding="utf-8"):
    m = re.match(r"^'(.)'\s*=", line)
    if m:
        known.add(m.group(1))

def split_comment(line):
    inq = False; i = 0
    while i < len(line):
        c = line[i]
        if c == '\\' and inq: i += 2; continue
        if c == '"': inq = not inq
        elif not inq and line.startswith("//", i): return line[:i], line[i:]
        i += 1
    return line, ""

strlit = re.compile(r'"(?:[^"\\]|\\.)*"')
def fix(code):
    def sub(m):
        return "".join(ch if (ord(ch) < 128 or ch in known) else "?" for ch in m.group(0))
    return strlit.sub(sub, code)

total = 0
for root in ("src", "data", "include"):
    for p in pathlib.Path(root).rglob("*"):
        if p.suffix not in (".c", ".h", ".inc", ".s", ".pory"): continue
        try: text = p.read_text(encoding="utf-8")
        except Exception: continue
        out = []; changed = 0
        for ln, line in enumerate(text.split("\n"), 1):
            if line.lstrip().startswith("//") or not any(ord(c) > 127 for c in line):
                out.append(line); continue
            code, com = split_comment(line)
            new = fix(code)
            if new != code:
                changed += 1
                print(f"{p}:{ln}: {code.strip()[:70]}  ->  {new.strip()[:70]}")
            out.append(new + com)
        if changed:
            total += changed
            if apply: p.write_text("\n".join(out), encoding="utf-8")
print(f"\n{total} line(s) {'changed' if apply else 'would change'}")
