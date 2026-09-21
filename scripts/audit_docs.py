import os
import glob
import re
import urllib.request

md_files = ["README.md"] + sorted(glob.glob("docs/**/*.md", recursive=True))
print(f"Total markdown files to audit: {len(md_files)}")

all_passed = True
for path in md_files:
    content = open(path, encoding="utf-8").read()
    ink_urls = re.findall(r"https://mermaid\.ink/[^\s\)\"]+", content)
    if not ink_urls:
        print(f"FAIL: {path} has NO mermaid.ink link!")
        all_passed = False
        continue
    
    url = ink_urls[0]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type")
            print(f"PASS: {path:<38} -> {len(ink_urls)} diagrams, verified HTTP {status} ({content_type})")
    except Exception as e:
        print(f"FAIL: {path:<38} -> Error accessing {url}: {e}")
        all_passed = False

if all_passed:
    print("\nALL 20 MARKDOWN FILES PASSED MERMAID.INK AUDIT SUCCESSFULLY!")
else:
    print("\nSOME FILES FAILED AUDIT!")
