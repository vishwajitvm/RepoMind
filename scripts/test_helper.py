import os
import base64
import sys

def make_mermaid_link(mermaid_code: str, alt_text: str = "Architecture Flow Diagram") -> str:
    clean_code = mermaid_code.strip()
    b64 = base64.b64encode(clean_code.encode("utf-8")).decode("ascii")
    url = f"https://mermaid.ink/svg/{b64}"
    return f"![{alt_text}]({url})\n\n```mermaid\n{clean_code}\n```"

print("Helper defined successfully.")
