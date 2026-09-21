import os
import base64
import urllib.request
import time

def make_mermaid_link(mermaid_code: str, alt_text: str = "Architecture Flow Diagram") -> str:
    clean = mermaid_code.strip()
    b64 = base64.b64encode(clean.encode("utf-8")).decode("ascii")
    url = f"https://mermaid.ink/svg/{b64}"
    return f"![{alt_text}]({url})\n\n```mermaid\n{clean}\n```"

def write_doc(rel_path: str, content: str):
    full_path = os.path.join(os.getcwd(), rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated {rel_path} ({len(content)} bytes)")

print("Docs builder initialized.")
